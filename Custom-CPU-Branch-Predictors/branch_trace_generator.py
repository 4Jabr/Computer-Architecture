# Branch Trace Generator with Command Line Arguments for Branches and Seed
import random
import argparse


class BranchTraceGenerator:
    @staticmethod
    def generate_trace(num_branches=10000, file_name="branch_trace.csv", seed=None):
        if seed is not None:
            random.seed(seed)
        with open(file_name, 'w') as file:
            file.write("BranchAddress,Outcome\n")  # Header
            for _ in range(num_branches):
                address = random.randint(0, 0xFFFF)
                outcome = random.randint(0, 1)
                file.write(f"{address},{outcome}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Branch Trace Generator")
    parser.add_argument("--trace", type=str, default="branch_trace.csv",
                        help="path to the branch trace file (default to branch_trace.csv)")
    parser.add_argument("--branches", type=int, default=10000,
                        help="Number of branches to generate")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for trace generation")
    args = parser.parse_args()

    BranchTraceGenerator.generate_trace(
        num_branches=args.branches, file_name=args.trace, seed=args.seed)
