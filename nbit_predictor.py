class nBitPredictor:
    def __init__(self, bits, start_state):
        self.bits = bits
        self.state = start_state
        self.mispredicted = 0
        self.total_predicted = 0

    
    def update(self, actual_direction):
        self.total_predicted += 1
        if actual_direction != self.prediction_bit():
            self.mispredicted += 1
        if actual_direction == 1:
            if self.state < (2 ** self.bits - 1):
                self.state += 1
        else:
            if self.state > 0:
                self.state -= 1

    def prediction(self):
        return "T" if self.state & (1 << (self.bits - 1)) else "NT"

    def prediction_bit(self):
        return 1 if self.state & (1 << (self.bits - 1)) else 0

    def getState(self):
        return format(self.state, f'0{self.bits}b')

    # Misprediction rate for each predictor, not for each branch instruction
    def misprediction_rate(self):
        return "{} out of {} ({:.2f}%)".format(
                self.mispredicted, 
                self.total_predicted, 
                float(self.mispredicted) / self.total_predicted * 100)
    
class nBitAgreePredictor(nBitPredictor):
    def update(self, bias, actual_direction):
        if actual_direction == bias:
            if self.state < 2 ** bits - 1:
                self.state += 1
        else:
            if self.state > 0:
                self.state -= 1

class PatternHistoryRegister():
    def __init__(self, size, start_state):
        self.size = size
        self.register = start_state
    
    def update(self, direction):
        self.register = (self.register << 1) | direction
        if self.register >= 2 ** self.size:
            self.register -= 2 ** self.size
    
    def get_value(self):
        return self.register
    
    def get_text(self):
        return format(self.register, f'0{self.size}b')