import tkinter as tk
from tkinter import ttk
from predictor_components import nBitPredictor, PatternHistoryRegister
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
        # self.name = options.pop("name")
        self.index_size = options.pop("index_size")
        predictor = options.pop("predictor")
        self.table = [copy.deepcopy(predictor) for _ in range((2 ** self.index_size))]

        self.prediction_stats = {}

        tk.Frame.__init__(self, parent, **options)

        self.table_frame = TableWidget(self, column_names=['Index','State','Prediction'])
        self.table_frame.pack()

        for i in range(len(self.table)):
            entry = [format(i, f'0{self.index_size}b'), self.table[i].getState(), self.table[i].prediction()]
            self.table_frame.add_row(entry)

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
        entry = [format(i, f'0{self.index_size}b'), self.table[i].getState(), self.table[i].prediction()]
        self.table_frame.set_row_at_index(i, entry)
        self.table_frame.set_focus(i)

    def stats(self, pc):
        return "{} out of {} ({:.2f}%)".format(
                self.prediction_stats[pc]['mispredicted'], 
                self.prediction_stats[pc]['total'], 
                float(self.prediction_stats[pc]['mispredicted']) / self.prediction_stats[pc]['total'] * 100)
    
class GHRPredictorWidget(BHTWidget):
    def __init__(self, parent, **options):
        ghr_size = options.pop("ghr_size")
        self.ghr = PatternHistoryRegister(ghr_size, 0)
        BHTWidget.__init__(self, parent, **options, index_size=ghr_size)

        tk.Label(self, text="Global History Register").pack()
        self.ghr_text = tk.Label(self, text=self.ghr.get_text())
        self.ghr_text.pack()

        columns = [
            'PC',
            'GHR',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
        self.history_table = TableWidget(self, column_names=columns)
        self.history_table.pack()

    def update(self, pc, direction):
        i = self.ghr.get_value()

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
        BHTWidget.__init__(self, parent, **options)

        tk.Label(self, text="Global History Register").pack()
        self.ghr_text = tk.Label(self, text=self.ghr.get_text())
        self.ghr_text.pack()

        columns = [
            'PC',
            'PC bits for indexing',
            'GHR',
            'PC bits XOR GHR',
            'Predicted',
            'Actual',
            'Misprediction Rate for this PC'
        ]
        self.history_table = TableWidget(self, column_names=columns)
        self.history_table.pack()

    def update(self, pc, direction):
        pc_i = pc & ((2 ** self.index_size) - 1)
        i = pc_i ^ (self.ghr.get_value() & (2 ** self.index_size - 1))

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

class TableWidget(ttk.Frame):
    def __init__(self, parent, **options):
        self.column_names = options.pop("column_names")
        super().__init__(parent, **options)
        cols = [i for i in range(len(self.column_names))]
        self.index = 0

            
        self.table = ttk.Treeview(self, columns=cols, show='headings')
        for col in cols:
            self.table.heading(col, text=self.column_names[col])
            self.table.column(col, minwidth=0, width=4*len(self.column_names[col])+80)
        
        self.table.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def add_row(self, entry):
        self.table.insert('', tk.END, id=self.index, values=entry, tags=("all"))
        self.index += 1

    def set_row_at_index(self, index, entry):
        self.table.item(index, values=entry)

    def set_focus(self, index):
        for i in range(self.index):
            self.table.item(i, tags='all')
        self.table.item(index, tags='focus')
        self.table.tag_configure('all', background='white')
        self.table.tag_configure('focus', background='green')

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