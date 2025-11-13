import csv
import time
import os
import argparse
from branch_predictors import StaticPredictor, OneBitBranchPredictor, TwoBitBranchPredictor, BimodalBranchPredictor, GShareBranchPredictor, HybridBranchPredictor
from tabulate import tabulate
import matplotlib.pyplot as plt

import numpy as np


class BranchPredictorSimulator:
    def __init__(self, trace_file="branch_trace.csv", visualize=False, x=10, fast=False):
        self.trace_file = trace_file
        self.x = x  # Number of instructions for accuracy calculation
        self.fast = fast  # Skip pauses if fast mode is enabled
        self.predictors = {
            "Static Taken": StaticPredictor(always_taken=True),
            "Static Not Taken": StaticPredictor(always_taken=False),
            "One Bit": OneBitBranchPredictor(),
            "Two Bit": TwoBitBranchPredictor(),
            "Bimodal": BimodalBranchPredictor(),
            "GShare": GShareBranchPredictor(),
            "Hybrid": HybridBranchPredictor()
        }
        self.stats = {name: [] for name in self.predictors}
        self.realtime_log_file = "realtime_stats.txt"
        if not os.path.exists("logs"):
            os.makedirs("logs")
        with open(self.realtime_log_file, 'w') as f:
            f.write("Predictor, Branches Processed, Cumulative Accuracy (%)\n")

        # For plotting
        self.visualize = visualize

    def run_simulation(self):
        branch_counts = {name: [] for name in self.predictors}
        accuracy_values = {name: [] for name in self.predictors}

        with open(self.trace_file, 'r') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader):
                address = int(row['BranchAddress'])
                outcome = int(row['Outcome'])
                for name, predictor in self.predictors.items():
                    prediction = predictor.predict(address)
                    correct = 1 if prediction == outcome else 0
                    predictor.update(address, outcome)
                    self.stats[name].append(correct)
                    branch_counts[name].append(row_num + 1)
                    accuracy = (sum(self.stats[name]) / (row_num + 1)) * 100
                    accuracy_values[name].append(accuracy)
                    self.log_statistics(name, row_num + 1, correct)

                if (row_num + 1) % self.x == 0:
                    self.display_progress(row_num + 1, address)
                    if not self.fast:
                        # Pause for 2 seconds after every x instructions
                        time.sleep(2)

        self.save_bht()
        self.display_final_accuracy()
        self.plot_accuracy(branch_counts, accuracy_values)

            

    def plot_accuracy(self, branch_counts, accuracy_values):
        
        plt.figure(figsize=(14, 7))
        for name in self.predictors:
            if branch_counts[name] and accuracy_values[name]:  # Check if data exists
                plt.plot(branch_counts[name], accuracy_values[name], label=name)

        plt.xlabel('Number of Branches')
        plt.ylabel('Prediction Accuracy (%)')
        plt.title('Branch Predictor Accuracy Over Time')
        plt.legend()
        plt.grid(True)
        
        print("Saving plot to file...")
        plt.savefig('branch_predictor_accuracy.png')  

    def log_statistics(self, predictor_name, branch_num, correct):
        log_file = f"logs/{predictor_name}_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"Branch: {branch_num}, Correct: {correct}\n")

    def display_progress(self, branches_processed, current_address):
        table_data = []
        for name, results in self.stats.items():
            cumulative_accuracy = (
                sum(results) / len(results)) * 100 if results else 0.0
            table_data.append([name, branches_processed, cumulative_accuracy])
        headers = ["Predictor", "Branches Processed",
                   "Cumulative Accuracy (%)"]
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Processing Branch Address: {current_address}")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        with open(self.realtime_log_file, 'a') as f:
            for row in table_data:
                f.write(f"{row[0]}, {row[1]}, {row[2]}\n")

    def save_bht(self):
        if not os.path.exists("bht_logs"):
            os.makedirs("bht_logs")
        for name, predictor in self.predictors.items():
            if hasattr(predictor, 'bht'):
                bht_file = f"bht_logs/{name}_bht.txt"
                with open(bht_file, 'w') as f:
                    if isinstance(predictor.bht, dict):
                        for address, value in predictor.bht.items():
                            f.write(f"Address: {address}, Value: {value}\n")
                    elif isinstance(predictor.bht, list):
                        for index, value in enumerate(predictor.bht):
                            f.write(f"Index: {index}, Value: {value}\n")

    def display_final_accuracy(self):
        table_data = []
        for name, results in self.stats.items():
            total_branches = len(results)
            accuracy = (sum(results) / total_branches) * \
                100 if total_branches > 0 else 0.0
            table_data.append([name, total_branches, accuracy])
        headers = ["Predictor", "Total Branches Processed",
                   "Overall Accuracy (%)"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Branch Predictor Simulator")
    parser.add_argument("--trace", type=str, default="branch_trace.csv",
                        help="path to the branch trace file (default to branch_trace.csv)")
    parser.add_argument("--x", type=int, default=10,
                        help="Number of instructions for per-interval accuracy calculation")
    parser.add_argument("--fast", action="store_true",
                        help="Skip pauses and run the simulation quickly")
    parser.add_argument("--visualize", action="store_true",
                        help="Visualize accuracy over time with plots")
    args = parser.parse_args()

    simulator = BranchPredictorSimulator(
        trace_file=args.trace, x=args.x, fast=args.fast, visualize=args.visualize)

    simulator.run_simulation()
