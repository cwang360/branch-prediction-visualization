import tkinter as tk
from tkinter import ttk
from nbit_predictor import nBitPredictor

class PredictorWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.name = options.pop("name")
        self.predictor = options.pop("predictor")
        self.history = [["Predicted: ", "Actual: "]]
        self.mispredicted = 0

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
        for i in range(len(self.history)):
            for j in range(2): 
                e = tk.Label(self.history_table, text=self.history[i][j])
                e.grid(row=j, column=i)

        self.misprediction_stats = tk.Label(self)
        self.misprediction_stats.pack()

    def update(self, d):
        predicted = self.predictor.prediction()
        actual = 'T' if d == 1 else 'NT'
        self.history.append([predicted, actual])
        if predicted is not actual:
            self.mispredicted += 1
        self.predictor.update(d)

        # Update GUI
        self.prediction_label.config(text = self.predictor.prediction())
        self.state_label.config(text = self.predictor.getState())

        tk.Label(self.history_table, text=self.history[len(self.history)-1][0]).grid(row=0, column=len(self.history)-1)
        tk.Label(self.history_table, text=self.history[len(self.history)-1][1]).grid(row=1, column=len(self.history)-1)

        self.misprediction_stats.config(
            text = "Misprediction rate: {} out of {} ({:.2f}%)".format(
                self.mispredicted, 
                len(self.history) - 1, 
                float(self.mispredicted) / (len(self.history) - 1) * 100))

class BHTWidget(tk.Frame):
    def __init__(self, parent, **options):
        self.name = options.pop("name")
        self.index_size = options.pop("index_size")
        self.table = [options.pop("predictor")] * (2 ** self.index_size)

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

    def update(self, i, direction):
        self.table[i].update(direction)
        tk.Label(self.table_frame, text=format(i, f'0{self.index_size}b')).grid(row=i+1, column=0)
        tk.Label(self.table_frame, text=self.table[i].getState()).grid(row=i+1, column=1)
        tk.Label(self.table_frame, text=self.table[i].prediction()).grid(row=i+1, column=2)

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