import _tkinter
import tkinter as tk
from tkinter import ttk
from nbit_predictor import nBitPredictor
from custom_widgets import *

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Branch Prediction Visualizer")
        self.master.geometry("600x600")
        self.inner = tk.Frame(self.master)
        self.inner.pack(fill="both", expand=True)
        self.pack()
        self.initial_screen()

    def initial_screen(self):
        self.clear()
        tk.Button(self.inner, text = "Compare simple n-bit predictors", command = self.simple_n_bit_predictor).pack()
        tk.Button(self.inner, text = "Branch History Table", command = self.branch_history_table).pack()

    def simple_n_bit_predictor(self):
        self.clear()
        self.predictor_widgets = [
            PredictorWidget(self.inner, name="1-bit predictor", predictor=nBitPredictor(1, 0b0)),
            PredictorWidget(self.inner, name="2-bit predictor", predictor=nBitPredictor(2, 0b00)),
        ]
        for widget in self.predictor_widgets:
            widget.pack(fill="both", expand=True)

        tk.Button(self.inner, text = "T", command = lambda : update(1)).pack()
        tk.Button(self.inner, text = "NT", command = lambda : update(0)).pack()

        def update(d):
            for widget in self.predictor_widgets:
                widget.update(d)
    
        tk.Button(self.inner, text = "Back", command = self.initial_screen).pack()

    def branch_history_table(self):  
        self.clear()
        input_history = []
        index_size = 3
        bht = BHTWidget(self.inner, name="Branch History Table", predictor=nBitPredictor(2, 0b00), index_size=index_size)
        bht.pack(fill="x", expand=True)
        tk.Button(self.inner, text = "Back", command = self.initial_screen).pack()

        tk.Label(self.inner, text = "Add a branch address (in binary) and actual direction").pack()
        pc_entry = tk.Entry(self.inner)
        pc_entry.pack()
        direction_entry = ttk.Combobox(self.inner, state = "readonly", values = ["Taken", "Not Taken"])
        direction_entry.pack()
        
        self.scrollable = ScrollableFrameY(self.master)
        history_table = tk.Frame(self.scrollable.scrollable_frame)
        history_table.pack(fill="both", expand=True)
        self.scrollable.pack(fill="both", expand=True)


        def update():
            direction = 1 if direction_entry.get() == "Taken" else 0
            index = int(pc_entry.get(), 2) & ((2 ** index_size) - 1)
            input_history.append([index, direction])
            tk.Label(history_table, text=pc_entry.get()).grid(row=len(input_history)-1, column=0)
            tk.Label(history_table, text=direction_entry.get()).grid(row=len(input_history)-1, column=1)
            bht.update(index, direction)

        submit = tk.Button(self.inner, text = "Submit", command = update)
        submit.pack(padx = 3, pady = 3)

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        try:
            self.scrollable.destroy()
        except:
            pass

    
root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI