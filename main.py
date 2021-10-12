import _tkinter
import tkinter as tk
from nbit_predictor import nBitPredictor
from custom_widgets import PredictorWidget

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Branch Prediction Visualizer")
        self.master.geometry("500x500")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.predictor_widgets = [
            PredictorWidget(self.master, name="1-bit predictor", predictor=nBitPredictor(1, 0b0)),
            PredictorWidget(self.master, name="2-bit predictor", predictor=nBitPredictor(2, 0b00)),
        ]
        for widget in self.predictor_widgets:
            widget.pack()

        predictT = tk.Button(self.master, text = "T", command = lambda : self.update(1)).pack()
        predictNT = tk.Button(self.master, text = "NT", command = lambda : self.update(0)).pack()

    def update(self, d):
        for widget in self.predictor_widgets:
            widget.update(d)
    
root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI