# Branch Predictor Implementations

# Static Predictor
class StaticPredictor:
    def __init__(self, always_taken=True):
        self.always_taken = always_taken

    def predict(self, address):
        return 1 if self.always_taken else 0  

    def update(self, address, actual_outcome):
        pass

# One-Bit Branch Predictor
class OneBitBranchPredictor:
    def __init__(self):
        self.history = {}  
    def predict(self, address):
        
        return self.history.get(address, 1)  
    def update(self, address, actual_outcome):
        if address not in self.history:
            self.history[address] = 1 if actual_outcome == 1 else 0
        else:
            self.history[address] = actual_outcome  

# Two-Bit Branch Predictor
class TwoBitBranchPredictor:
    def __init__(self):
        self.history = {}  # Stores the state for each branch address (2-bit)

    def predict(self, address):
        # Return the most significant bit for prediction (00, 01, 10, 11)
        return self.history.get(address, 2) > 1  

    def update(self, address, actual_outcome):
        if address not in self.history:
            
            self.history[address] = 2 if actual_outcome == 1 else 0
        else:
            state = self.history[address]
            if actual_outcome == 1:
                
                self.history[address] = min(state + 1, 3)
            else:
                
                self.history[address] = max(state - 1, 0)

# Bimodal Branch Predictor
class BimodalBranchPredictor:
    def __init__(self, table_size=1024):
        self.table_size = table_size
        self.bht = [1] * table_size  # Initialize with weakly taken state

    def predict(self, address):
        index = address % self.table_size
        return self.bht[index] > 1  # 1 or 2 indicates 'taken', 0 or 1 indicates 'not taken'

    def update(self, address, actual_outcome):
        index = address % self.table_size
        if actual_outcome == 1:
            # Increment state but don't exceed '11'
            self.bht[index] = min(self.bht[index] + 1, 3)
        else:
            # Decrement state but don't go below '00'
            self.bht[index] = max(self.bht[index] - 1, 0)

# GShare Branch Predictor
class GShareBranchPredictor:
    def __init__(self, history_bits=10):
        self.history_bits = history_bits
        self.global_history = 0  
        self.table_size = 2 ** history_bits
        self.bht = [1] * self.table_size  

    def predict(self, address):
        index = (address ^ self.global_history) % self.table_size
        return self.bht[index] > 1  

    def update(self, address, actual_outcome):
        index = (address ^ self.global_history) % self.table_size
        if actual_outcome == 1:
            self.bht[index] = min(self.bht[index] + 1, 3)
        else:
            self.bht[index] = max(self.bht[index] - 1, 0)

        
        self.global_history = ((self.global_history << 1) | actual_outcome) % (2 ** self.history_bits)

# Hybrid Branch Predictor
class HybridBranchPredictor:
    def __init__(self, history_bits=10, table_size=1024):
        self.history_bits = history_bits
        self.global_history = 0
        self.bht = [1] * table_size  
        self.predictor1 = BimodalBranchPredictor(table_size)
        self.predictor2 = GShareBranchPredictor(history_bits)
        self.selector = [1] * table_size  

    def predict(self, address):
        index = (address ^ self.global_history) % len(self.selector)
        if self.selector[index] > 1:  
            return self.predictor2.predict(address)
        else:  
            return self.predictor1.predict(address)

    def update(self, address, actual_outcome):
        index = (address ^ self.global_history) % len(self.selector)
        prediction = self.predict(address)

        
        if prediction != actual_outcome:
            if self.selector[index] > 1:
                self.selector[index] = max(self.selector[index] - 1, 0)  
            else:
                self.selector[index] = min(self.selector[index] + 1, 3)  

        
        self.global_history = ((self.global_history << 1) | actual_outcome) % (2 ** self.history_bits)

        
        self.predictor1.update(address, actual_outcome)
        self.predictor2.update(address, actual_outcome)
