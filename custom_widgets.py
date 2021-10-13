import tkinter as tk
from tkinter import ttk
from nbit_predictor import nBitPredictor
import copy

class PredictorWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.name = options.pop("name")
        self.predictor = options.pop("predictor")

        tk.Frame.__init__(self, parent, **options)

        tk.Label(self, text = self.name).pack()

        self.state_label = tk.Label(self, text = self.predictor.getState())
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
        self.state_label.config(text = self.predictor.getState())

        tk.Label(self.history_table, text=predicted).grid(row=0, column=self.predictor.total_predicted)
        tk.Label(self.history_table, text=actual).grid(row=1, column=self.predictor.total_predicted)

        self.misprediction_stats.config(text = "Misprediction rate: " + self.predictor.misprediction_rate())

class BHTWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.name = options.pop("name")
        self.index_size = options.pop("index_size")
        predictor = options.pop("predictor")
        self.table = [copy.deepcopy(predictor) for _ in range((2 ** self.index_size))]

        self.prediction_stats = {}

        tk.Frame.__init__(self, parent, **options)

        self.table_label = tk.Label(self, text = self.name)
        self.table_label.pack(fill="x", expand=True)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack()

        tk.Label(self.table_frame, text="Index").grid(row=0, column=0)
        tk.Label(self.table_frame, text="State").grid(row=0, column=1)
        tk.Label(self.table_frame, text="Prediction").grid(row=0, column=2)
        for i in range(len(self.table)):
            tk.Label(self.table_frame, text=format(i, f'0{self.index_size}b')).grid(row=i+1, column=0)
            tk.Label(self.table_frame, text=self.table[i].getState()).grid(row=i+1, column=1)
            tk.Label(self.table_frame, text=self.table[i].prediction()).grid(row=i+1, column=2)

    def update(self, pc, i, direction):
        # i is index of BHT!
        predicted = self.table[i].prediction()
        actual = 'T' if direction == 1 else 'NT'

        if pc not in self.prediction_stats:
            self.prediction_stats[pc] = {'total': 0, 'mispredicted': 0}
        self.prediction_stats[pc]['total'] += 1 
        if predicted is not actual:
            self.prediction_stats[pc]['mispredicted'] += 1

        self.table[i].update(direction)
        tk.Label(self.table_frame, text=format(i, f'0{self.index_size}b')).grid(row=i+1, column=0)
        tk.Label(self.table_frame, text=self.table[i].getState()).grid(row=i+1, column=1)
        tk.Label(self.table_frame, text=self.table[i].prediction()).grid(row=i+1, column=2)

class GShareWidget(BHTWidget):
    def __init__(self, parent, **options):
        self.ghr_size = options.pop("ghr_size")
        BHTWidget.__init__(self, parent, **options)

        self.ghr = 0
    def update(self, pc, direction):
        pc_i = pc & ((2 ** self.index_size) - 1)
        i = pc_i ^ (self.ghr & (2 ** self.index_size - 1))

        self.ghr = (self.ghr << 1) | direction
        if self.ghr >= 2 ** self.ghr_size:
            self.ghr -= 2 ** self.ghr_size

        prediction = self.table[i].prediction()

        BHTWidget.update(self, pc, i, direction)

        entry = [
            format(pc, 'b'),
            format(pc_i, f'0{self.index_size}b'),
            format(i, f'0{self.index_size}b'),
            prediction,
            'T' if direction == 1 else 'NT',
            "{} out of {} ({:.2f}%)".format(
                self.prediction_stats[pc]['mispredicted'], 
                self.prediction_stats[pc]['total'], 
                float(self.prediction_stats[pc]['mispredicted']) / self.prediction_stats[pc]['total'] * 100)
        ]
         
        return entry

    def get_ghr(self):
        return format(self.ghr, f'0{self.ghr_size}b')

class ScrollableFrameX(ttk.Frame):
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

class ScrollableFrameY(ttk.Frame):
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")