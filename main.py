import _tkinter
import tkinter as tk
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
        BHTWidget(self.master, name="Branch History Table", predictor=nBitPredictor(2, 0b00), index_size=3).pack()
        tk.Button(self.master, text = "Back", command = self.initial_screen).pack()
        
    def clear_master(self):
        for widget in self.master.winfo_children():
            widget.destroy()  
    
root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI