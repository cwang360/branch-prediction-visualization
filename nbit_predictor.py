class nBitPredictor:
    def __init__(self, bits, start_state):
        self.bits = bits
        self.state = start_state
    
    def update(self, actual_direction):
        if actual_direction == 1:
            if self.state < (2 ** self.bits - 1):
                self.state += 1
        else:
            if self.state > 0:
                self.state -= 1

    def prediction(self):
        return "T" if self.state & (1 << (self.bits - 1)) else "NT"

    def getState(self):
        return format(self.state, f'0{self.bits}b')

class nBitAgreePredictor(nBitPredictor):
    def __init__(self, bits, start_state):
        nBitPredictor.__init__(self, bits, start_state)
        self.bias = -1

    def update(self, actual_direction):
        if self.bias == -1:
            self.bias = actual_direction

        if actual_direction == bias:
            if self.state < 2 ** bits - 1:
                self.state += 1
        else:
            if self.state > 0:
                self.state -= 1