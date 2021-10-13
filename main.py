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
        self.master.geometry("500x500")
        self.pack()
        self.initial_screen()

    def initial_screen(self):
        self.clear_master()
        tk.Button(self.master, text = "Compare simple n-bit predictors", command = self.simple_n_bit_predictor).pack()
        tk.Button(self.master, text = "Branch History Table", command = self.branch_history_table).pack()

    def simple_n_bit_predictor(self):
        self.clear_master()
        self.predictor_widgets = [
            PredictorWidget(self.master, name="1-bit predictor", predictor=nBitPredictor(1, 0b0)),
            PredictorWidget(self.master, name="2-bit predictor", predictor=nBitPredictor(2, 0b00)),
        ]
        for widget in self.predictor_widgets:
            widget.pack()

        tk.Button(self.master, text = "T", command = lambda : update(1)).pack()
        tk.Button(self.master, text = "NT", command = lambda : update(0)).pack()

        def update(d):
            for widget in self.predictor_widgets:
                widget.update(d)
    
        tk.Button(self.master, text = "Back", command = self.initial_screen).pack()

    def branch_history_table(self):  
        self.clear_master()
        index_size = 3
        bht = BHTWidget(self.master, name="Branch History Table", predictor=nBitPredictor(2, 0b00), index_size=index_size)
        bht.pack()
        tk.Button(self.master, text = "Back", command = self.initial_screen).pack()

        tk.Label(self.master, text = "Add a branch address (in binary) and actual direction").pack()
        pc_entry = tk.Entry(self.master)
        pc_entry.pack()
        direction_entry = ttk.Combobox(self.master, state = "readonly", values = ["Taken", "Not Taken"])
        direction_entry.pack()

        def update():
            direction = 1 if direction_entry.get() == "Taken" else 0
            index = int(pc_entry.get(), 2) & ((2 ** index_size) - 1)
            bht.update(index, direction)

        submit = tk.Button(self.master, text = "Submit", command = update)
        submit.pack(padx = 3, pady = 3)



        
    def clear_master(self):
        for widget in self.master.winfo_children():
            widget.destroy()  
    
root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI