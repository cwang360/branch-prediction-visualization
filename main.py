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
        self.master.geometry("1200x700")
        self.inner = tk.Frame(self.master)
        self.inner.pack(fill="both", expand=True)
        self.pack()
        self.initial_screen()

    def initial_screen(self):
        self.clear()
        tk.Button(self.inner, text = "Compare simple n-bit saturating counters", command = self.simple_n_bit_predictor).pack()
        tk.Button(self.inner, text = "Simulate a custom branch predictor", command = self.choose_bht_entries).pack()

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

    def choose_bht_entries(self):
        self.clear()
        tk.Label(self.inner, text = "Choose BHT entry type and counter size").pack()

        num_bits_entry = tk.Entry(self.inner)
        num_bits_entry.insert(0, "Number of bits (int)")
        num_bits_entry.pack()

        bht_type_entry = ttk.Combobox(
            self.inner, 
            state = "readonly", 
            values = ["-bit saturating counter", 
                    "-bit agree predictor (designed to reduce negative interference with aliasing)"])
        bht_type_entry.pack()

        img = tk.PhotoImage(file='assets/bht_entry_choices.png')
        image_panel = tk.Label(self.inner, image = img)
        image_panel.image = img
        image_panel.pack(side = "bottom", fill = "both", expand = "yes")

        def next():
            self.num_bits = num_bits_entry.get()
            self.bht_type = bht_type_entry.get()
            self.choose_indexing_method()

        tk.Button(self.inner, text = "Next", command = next).pack(padx = 3, pady = 3)

        
    def choose_indexing_method(self):
        self.clear()
        tk.Label(self.inner, text = "Choose BHT indexing method").pack()
        indexing_method_entry = ttk.Combobox(
            self.inner, 
            state = "readonly", 
            values = ["PC", 
                    "GHR",
                    "GShare",
                    "PShare"])
        indexing_method_entry.pack()

        img = tk.PhotoImage(file='assets/indexing_choices.png')
        image_panel = tk.Label(self.inner, image = img)
        image_panel.image = img
        image_panel.pack(side = "bottom", fill = "both", expand = "yes")

        def next():
            self.indexing_method = indexing_method_entry.get()
            self.branch_history_table()

        tk.Button(self.inner, text = "Next", command = next).pack(padx = 3, pady = 3)


    def branch_history_table(self):  
        self.clear()
        index_size = 3
        bht = GShareWidget(self.inner, name="Branch History Table", ghr_size=5, predictor=nBitPredictor(2, 0b00), index_size=index_size)
        bht.pack(fill="x", expand=True)

        ghr = tk.Label(self.inner, text=bht.get_ghr())
        ghr.pack()

        tk.Button(self.inner, text = "Back", command = self.initial_screen).pack()

        tk.Label(self.inner, text = "Add a branch address (in binary) and actual direction").pack()
        pc_entry = tk.Entry(self.inner)
        pc_entry.pack()
        direction_entry = ttk.Combobox(self.inner, state = "readonly", values = ["Taken", "Not Taken"])
        direction_entry.pack()
        
        self.history_table = ttk.Treeview(self.master, columns=('1', '2', '3', '4', '5', '6'), show='headings')
        self.history_table.heading('1', text='PC')
        self.history_table.heading('2', text='PC bits for indexing')
        self.history_table.heading('3', text='PC bits XOR GHR')
        self.history_table.heading('4', text='Predicted')
        self.history_table.heading('5', text='Actual')
        self.history_table.heading('6', text='Misprediction Rate')
        
        self.history_table.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.history_table.yview)
        self.history_table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")


        def update():
            direction = 1 if direction_entry.get() == "Taken" else 0
            entry = bht.update(int(pc_entry.get(), 2) , direction)
            
            self.history_table.insert('', tk.END, values=entry)

            ghr.config(text=bht.get_ghr())

        submit = tk.Button(self.inner, text = "Submit", command = update)
        submit.pack(padx = 3, pady = 3)

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.pack_forget()
        try:
            self.history_table.pack_forget()
            self.scrollbar.pack_forget()
        except:
            pass

    
root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI