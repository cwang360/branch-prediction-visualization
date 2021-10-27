import tkinter as tk
from tkinter import ttk
from predictor_components import *
from gui_widgets import TableWidget, ScrollableFrameX
import copy

class PredictorWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.name = options.pop("name")
        self.predictor = options.pop("predictor")

        tk.Frame.__init__(self, parent, **options)

        tk.Label(self, text = self.name).pack()

        self.state_label = tk.Label(self, text = self.predictor.get_state())
        self.state_label.pack()

        self.prediction_label = tk.Label(self, text = self.predictor.prediction())
        self.prediction_label.pack()

        self.scrollable = ScrollableFrameX(self)
        self.history_table = tk.Frame(self.scrollable.scrollable_frame)
        self.history_table.pack(fill="both", expand=True)
        self.scrollable.pack(fill="both", expand=True)
        
        tk.Label(self.history_table, text="Predicted: ").grid(row=0, column=0)
        tk.Label(self.history_table, text="Actual: ").grid(row=1, column=0)

        self.misprediction_stats = tk.Label(self)
        self.misprediction_stats.pack()

    def update(self, d):
        predicted = self.predictor.prediction()
        actual = 'T' if d == 1 else 'NT'
        self.predictor.update(d)

        # Update GUI
        self.prediction_label.config(text = self.predictor.prediction())
        self.state_label.config(text = self.predictor.get_state())

        tk.Label(self.history_table, text=predicted).grid(row=0, column=self.predictor.total_predicted)
        tk.Label(self.history_table, text=actual).grid(row=1, column=self.predictor.total_predicted)

        self.misprediction_stats.config(text = "Misprediction rate: " + self.predictor.misprediction_rate())

class NBitPredictorComparisonWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.predictors = options.pop("predictors")
        self.headings =  options.pop("headings")
        tk.Frame.__init__(self, parent, **options)

        self.info = TableWidget(self, height=2, column_names=["      "] + self.headings)
        self.outcomes = TableWidget(self, height=15, column_names=["Actual"] + self.headings)

        states = ["State"]
        for predictor in self.predictors:
            states.append(predictor.get_state())
        self.info.add_row(states)

        stats = ["Misprediction rate"]
        for predictor in self.predictors:
            states.append(predictor.misprediction_rate())
        self.info.add_row(stats)

        self.info.pack(fill="x", expand=True)
        self.outcomes.pack(fill="both", expand=True)

    def update(self, d):
        actual = 'T' if d == 1 else 'NT'

        states = ["State"]
        stats = ["Misprediction rate"]
        outcome = [actual]

        for predictor in self.predictors:
            outcome.append(predictor.prediction())
            predictor.update(d)
            states.append(predictor.get_state())
            stats.append(predictor.misprediction_rate())

        # Update GUI
        self.outcomes.add_row(outcome)
        self.info.set_row_at_index(0, states)
        self.info.set_row_at_index(1, stats)
      

class BHTWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.index_size = options.pop("index_size")
        predictor = options.pop("predictor")

        if "min_index" in options:
            self.min_index = options.pop("min_index")

        self.agree_predictor = isinstance(predictor, nBitAgreePredictor)
        self.table = [copy.deepcopy(predictor) for _ in range((1 << self.index_size))]

        self.prediction_stats = {}

        tk.Frame.__init__(self, parent, **options)

        self.top = tk.Frame(self)
        self.left = tk.Frame(self.top)
        self.right = tk.Frame(self.top)
        self.top.pack(fill="both", expand=True)
        self.left.pack(side="left", fill="both", expand=True)
        self.right.pack(side="right", fill="both", expand=True)


    def pack_all(self):
        self.bht_frame = tk.Frame(self.right)
        tk.Label(self.bht_frame, text="Branch History Table").pack()
        self.table_frame = TableWidget(self.bht_frame, column_names=['Index','State','Prediction'])
        self.table_frame.pack(fill="both", expand=True)
        self.bht_frame.pack(side="left", fill="both", expand=True)

        self.history_table = TableWidget(self, column_names=self.columns)
        self.history_table.pack(fill="both", expand=True)

        if self.agree_predictor:
            self.bias_table = BiasBitTableWidget(self.right)
            self.bias_table.pack(side="right", fill="both", expand=True)

        for i in range(len(self.table)):
            if self.agree_predictor:
                predicted = self.table[i].prediction(-1)
            else:
                predicted = self.table[i].prediction()
            entry = [format(i, f'0{self.index_size}b'), self.table[i].get_state(), predicted]
            self.table_frame.add_row(entry)

    def update(self, pc, i, direction):
        # i is index of BHT!
        if self.agree_predictor:
            predicted = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            predicted = self.table[i].prediction()

        actual = 'T' if direction == 1 else 'NT'

        if pc not in self.prediction_stats:
            self.prediction_stats[pc] = {'total': 0, 'mispredicted': 0}
        self.prediction_stats[pc]['total'] += 1 
        if predicted is not actual:
            self.prediction_stats[pc]['mispredicted'] += 1

        if self.agree_predictor:
            self.table[i].update(self.bias_table.get_or_set_bias(pc, direction), direction)
        else:
            self.table[i].update(direction)

        if self.agree_predictor:
            new_predicted = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            new_predicted = self.table[i].prediction()
        entry = [format(i, f'0{self.index_size}b'), self.table[i].get_state(), new_predicted]
        self.table_frame.set_row_at_index(i, entry)
        self.table_frame.set_focus(i)

    def stats(self, pc):
        return "{} out of {} ({:.2f}%)".format(
                self.prediction_stats[pc]['mispredicted'], 
                self.prediction_stats[pc]['total'], 
                float(self.prediction_stats[pc]['mispredicted']) / self.prediction_stats[pc]['total'] * 100)
    
class PHTWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.history_length = options.pop("history_length")
        self.index_size = options.pop('index_size')
        tk.Frame.__init__(self, parent, **options)

        self.pht = [copy.deepcopy(PatternHistoryRegister(self.history_length, 0)) for _ in range(1 << self.index_size)]

        tk.Label(self, text="Pattern History Table").pack()
        self.table_frame = TableWidget(self, column_names=['Index', 'Pattern History'])
        for i in range(len(self.pht)):
            entry = [format(i, f'0{self.index_size}b'),self.pht[i].get_text()]
            self.table_frame.add_row(entry)
        self.table_frame.pack(fill="both", expand=True)

    def update(self, i, direction):
        self.pht[i].update(direction)
        self.table_frame.set_row_at_index(i, [format(i, f'0{self.index_size}b'),self.pht[i].get_text()])
        self.table_frame.set_focus(i)

class BiasBitTableWidget(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent, **options)

        self.record = {}

        tk.Label(self, text="Bias Bit Table").pack()
        self.table_frame = TableWidget(self, column_names=['PC', 'Bias Bit'])
        self.table_frame.pack(fill="both", expand=True)

    def set_bias(self, pc, direction):
        if pc not in self.record:
            self.record[pc] = {
                "index" : len(self.record),
                "bias" : direction
            } 
            self.table_frame.add_row([format(pc, 'b'), direction])
            self.table_frame.set_focus(self.record[pc]["index"])

    def get_or_set_bias(self, pc, direction):
        if pc in self.record:
            self.table_frame.set_focus(self.record[pc]["index"])
            return self.record[pc]["bias"]
        else:
            self.set_bias(pc, direction)
            return 0
        
class LocalHistoryPredictorWidget(BHTWidget):
    def __init__(self, parent, **options):
        self.bht_index_size = options.pop("bht_index_size")
        self.pht_index_size = options.pop("pht_index_size")
        self.columns = [
            'PC',
            'PC bits for indexing',
            'PHT Entry',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
       
        BHTWidget.__init__(self, parent, index_size=self.bht_index_size, **options)
        self.pht_widget = PHTWidget(self.left, index_size=self.pht_index_size, history_length=self.bht_index_size)
        self.pht_widget.pack(fill="both", expand=True)
        self.pack_all()

        
    def update(self, pc, direction):
        mask = (1 << self.pht_index_size) - 1
        i = (pc & (mask << self.min_index)) >> self.min_index
        
        if self.agree_predictor:
            prediction = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, self.pht_widget.pht[i].get_value(), direction)

        entry = [
            format(pc, 'b'),
            format(i, f'0{self.pht_index_size}b'),
            self.pht_widget.pht[i].get_text(),
            prediction,
            'T' if direction == 1 else 'NT',
            self.stats(pc)
        ]
        
        self.pht_widget.update(i, direction)
        self.history_table.add_row(entry)

class PSharePredictorWidget(BHTWidget):
    def __init__(self, parent, **options):
        self.columns = [
            'PC',
            'PC bits for indexing',
            'PHT Entry',
            'PHT Entry XOR PC Bits',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
       
        BHTWidget.__init__(self, parent, **options)
        self.pht_widget = PHTWidget(self.left, index_size=self.index_size, history_length=self.index_size)
        self.pht_widget.pack(fill="both", expand=True)
        self.pack_all()

        
    def update(self, pc, direction):
        mask = (1 << self.index_size) - 1
        pc_i = (pc & (mask << self.min_index)) >> self.min_index
        i = pc_i ^ self.pht_widget.pht[pc_i].get_value()
        
        if self.agree_predictor:
            prediction = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, i, direction)

        entry = [
            format(pc, 'b'),
            format(pc_i, f'0{self.index_size}b'),
            self.pht_widget.pht[pc_i].get_text(),
            format(i, f'0{self.index_size}b'),
            prediction,
            'T' if direction == 1 else 'NT',
            self.stats(pc)
        ]
        
        self.pht_widget.update(pc_i, direction)
        self.history_table.add_row(entry)

class PCPredictorWidget(BHTWidget):
    def __init__(self, parent, **options):

        self.columns = [
            'PC',
            'PC bits for indexing',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
        BHTWidget.__init__(self, parent, **options)
        self.pack_all()
    def update(self, pc, direction):
        mask = (1 << self.index_size) - 1
        i = (pc & (mask << self.min_index)) >> self.min_index

        if self.agree_predictor:
            prediction = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, i, direction)

        entry = [
            format(pc, 'b'),
            format(i, f'0{self.index_size}b'),
            prediction,
            'T' if direction == 1 else 'NT',
            self.stats(pc)
        ]
        
        self.history_table.add_row(entry)

class GHRPredictorWidget(BHTWidget):
    def __init__(self, parent, **options):
        ghr_size = options.pop("ghr_size")
        self.ghr = PatternHistoryRegister(ghr_size, 0)
        self.columns = [
            'PC',
            'GHR',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
        BHTWidget.__init__(self, parent, **options, index_size=ghr_size)

        tk.Label(self.left, text="Global History Register").pack()
        self.ghr_text = tk.Label(self.left, text=self.ghr.get_text())
        self.ghr_text.pack()
        self.pack_all()
    def update(self, pc, direction):
        i = self.ghr.get_value()

        if self.agree_predictor:
            prediction = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, i, direction)

        entry = [
            format(pc, 'b'),
            self.ghr.get_text(),
            prediction,
            'T' if direction == 1 else 'NT',
            self.stats(pc)
        ]
        
        self.ghr.update(direction)
        self.ghr_text.config(text=self.ghr.get_text())
        self.history_table.add_row(entry)

class GSharePredictorWidget(BHTWidget):
    def __init__(self, parent, **options):
        self.ghr = PatternHistoryRegister(options.pop("ghr_size"), 0)
        self.columns = [
            'PC',
            'PC bits for indexing',
            'GHR',
            'PC bits XOR GHR',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
        BHTWidget.__init__(self, parent, **options)
        tk.Label(self.left, text="Global History Register").pack()
        self.ghr_text = tk.Label(self.left, text=self.ghr.get_text())
        self.ghr_text.pack()
        self.pack_all()

    def update(self, pc, direction):
        mask = (1 << self.index_size) - 1
        pc_i = (pc & (mask << self.min_index)) >> self.min_index
        i = pc_i ^ (self.ghr.get_value() & mask)

        if self.agree_predictor:
            prediction = self.table[i].prediction(self.bias_table.get_or_set_bias(pc, direction))
        else:
            prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, i, direction)

        entry = [
            format(pc, 'b'),
            format(pc_i, f'0{self.index_size}b'),
            self.ghr.get_text(),
            format(i, f'0{self.index_size}b'),
            prediction,
            'T' if direction == 1 else 'NT',
            self.stats(pc)
        ]
        
        self.ghr.update(direction)
        self.ghr_text.config(text=self.ghr.get_text())
        self.history_table.add_row(entry)

