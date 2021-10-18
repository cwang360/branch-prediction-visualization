import _tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from predictor_components import nBitPredictor, nBitAgreePredictor
from predictor_widgets import *
from gui_widgets import ImageWidget, ScrollableFrameY, DiscreteIntSpinbox


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Branch Prediction Visualizer")
        self.master.geometry("1000x700")
        self.inner = tk.Frame(self.master)
        self.inner.pack(fill="both", expand=True)
        self.pack()
        self.initial_screen()

    def initial_screen(self):
        self.clear()
        tk.Button(self.inner, text = "Compare simple n-bit saturating counters", command = self.simple_n_bit_predictor).pack()
        ImageWidget(self.inner, image_path="assets/n_bit_predictor.png").pack()
        tk.Button(self.inner, text = "Simulate a custom branch predictor", command = self.choose_bht_entries).pack()
        ImageWidget(self.inner, image_path="assets/general_architecture.png").pack()

    def simple_n_bit_predictor(self):
        self.clear()
        predictors = [nBitPredictor(1,0), nBitPredictor(2,0), nBitPredictor(3,0)]
        names = ["1-bit counter", "2-bit counter", "3-bit counter"]
        self.predictor_widget = NBitPredictorComparisonWidget(self.inner, predictors=predictors, headings=names)
        self.predictor_widget.pack(fill="x", expand=True)

        tk.Button(self.inner, text = "T", command = lambda : self.predictor_widget.update(1)).pack()
        tk.Button(self.inner, text = "NT", command = lambda : self.predictor_widget.update(0)).pack()
        
        tk.Button(self.inner, text = "Back", command = self.initial_screen).pack()

    def choose_bht_entries(self):
        self.clear()
        tk.Label(self.inner, text = "Choose BHT entry type and counter size").pack()

        entry_frame = tk.Frame(self.inner)
        num_bits_entry = DiscreteIntSpinbox(entry_frame, min=1, max=10)
        num_bits_entry.pack(side="left")

        bht_type_entry = ttk.Combobox(
            entry_frame, 
            state = "readonly", 
            values = ["-bit saturating counter", 
                    "-bit agree predictor"])
        bht_type_entry.pack(side="right")
        entry_frame.pack()

        def next():
            self.num_bits = int(num_bits_entry.get())
            self.bht_entry = nBitPredictor(self.num_bits, 0) if bht_type_entry.get() == "-bit saturating counter" else nBitAgreePredictor(self.num_bits, 0)
            self.choose_indexing_method()

        tk.Button(self.inner, text = "Next", command = next).pack(padx = 3, pady = 3)
        ImageWidget(self.inner, image_path="assets/bht_entry_choices.png").pack()

    def choose_indexing_method(self):
        self.clear()
        tk.Label(self.inner, text = "Choose BHT indexing method").pack()
        indexing_method_entry = ttk.Combobox(
            self.inner, 
            state = "readonly", 
            values = ["PC", 
                    "GHR",
                    "GShare",
                    "PShare",
                    "Local History"])
        indexing_method_entry.pack()

        def next():
            self.indexing_method = indexing_method_entry.get()
            self.choose_additional_settings()

        tk.Button(self.inner, text = "Next", command = next).pack(padx = 3, pady = 3)
        ImageWidget(self.inner, image_path="assets/indexing_choices.png").pack()

    def choose_additional_settings(self):
        self.clear()

        if self.indexing_method != "GHR":
            entry_frame = tk.Frame(self.inner)
            tk.Label(self.inner, text = "Choose bits of PC to use for indexing (lowest bit is bit 0):").pack()
            pc_min_index_entry = DiscreteIntSpinbox(entry_frame, min=0, max=63)
            pc_min_index_entry.grid(row=0, column=0)
            tk.Label(entry_frame, text = " to ").grid(row=0, column=1)
            pc_max_index_entry = DiscreteIntSpinbox(entry_frame, min=0, max=63)
            pc_max_index_entry.grid(row=0, column=2)
            entry_frame.pack()

        if self.indexing_method == "PC":
            tk.Label(self.inner, text = "These bits will be used to index BHT").pack()
        elif self.indexing_method == "GHR":
            tk.Label(self.inner, text = "GHR size (will be used to index BHT):").pack()
            bht_index_entry = DiscreteIntSpinbox(self.inner, min=1, max=64)
            bht_index_entry.pack()
        elif self.indexing_method == "GShare":
            tk.Label(self.inner, text = "GHR will have the same bit size as this range.").pack()
            tk.Label(self.inner, text = "These bits of PC will be used to XOR GHR to index BHT").pack()
        elif self.indexing_method == "Local History":
            tk.Label(self.inner, text = "This portion of PC will be used to index PHT").pack()
            tk.Label(self.inner, text = "BHT index size (BHT will have 2^(index size) entries):").pack()
            bht_index_entry = DiscreteIntSpinbox(self.inner, min=1, max=64)
            bht_index_entry.pack()
        elif self.indexing_method =="PShare":
            tk.Label(self.inner, text = "PHT index size and BHT index size will be the same as this range.").pack()
            tk.Label(self.inner, text = "These bits of PC will be used to XOR corresponding PHT entry to index BHT").pack()

        def next():
            self.pc_min_index = int(pc_min_index_entry.get())
            self.pc_max_index = int(pc_max_index_entry.get())
            self.pc_index_size = (self.pc_max_index - self.pc_min_index) + 1
            if self.indexing_method == "Local History":
                self.bht_index_size = int(bht_index_entry.get())
            self.branch_history_table()
        tk.Button(self.inner, text = "Next", command = next).pack(padx = 3, pady = 3)

    def branch_history_table(self):  
        self.clear()

        bht = self.get_predictor()
        bht.pack(fill="x", expand=True)

        tk.Button(self.inner, text = "Back", command = self.initial_screen).pack()

        tk.Label(self.inner, text = "Add a branch address (in binary) and actual direction").pack()
        pc_entry = tk.Entry(
            self.inner, 
            validate='key', 
            validatecommand=(self.register(lambda val : val in ["0", "1"]), '%S'))
        pc_entry.pack()
        direction_entry = ttk.Combobox(self.inner, state = "readonly", values = ["Taken", "Not Taken"])
        direction_entry.pack()
        
        def update():
            direction = 1 if direction_entry.get() == "Taken" else 0
            bht.update(int(pc_entry.get(), 2) , direction)

        submit = tk.Button(self.inner, text = "Submit", command = update)
        submit.pack(padx = 3, pady = 3)

        def simulate_from_file(event=None):
            filename = filedialog.askopenfilename()
            if not filename.endswith('.txt'):
                messagebox.showerror('Error', 'File must be .txt file')
                return
            with open(filename, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    try:
                        tokens = line.split()
                        direction = 1 if tokens[1] == "T" else 0
                        bht.update(int(tokens[0], 2), direction)
                    except:
                        messagebox.showerror('Error', 'File lines are not formatted properly. Each line must have PC and T/NT separated by whitespace.')
                        return
        tk.Label(self.inner, text = "Alternatively, select a text file to simulate.").pack()
        tk.Label(self.inner, text = "Each line in the file must start with a PC value and T/NT separated by whitespace.").pack()

        button = tk.Button(self.inner, text='Select File', command=simulate_from_file)
        button.pack()

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.pack_forget()

    def get_predictor(self):
        self.predictor_frame = tk.Frame(self.inner)
        self.predictor_frame.pack()
        if self.indexing_method == "PC":
            return PCPredictorWidget(
                self.predictor_frame, 
                index_size=self.pc_index_size, 
                predictor=self.bht_entry, 
                min_index=self.pc_min_index)
        elif self.indexing_method == "GHR":
            return GHRPredictorWidget(
                self.predictor_frame, 
                ghr_size=self.bht_index_size, 
                predictor=self.bht_entry)
        elif self.indexing_method == "GShare":
            return GSharePredictorWidget(
                self.predictor_frame, 
                ghr_size=self.pc_index_size, 
                predictor=self.bht_entry, 
                index_size=self.pc_index_size, 
                min_index=self.pc_min_index)
        elif self.indexing_method == "Local History":
            return LocalHistoryPredictorWidget(
                self.predictor_frame, 
                predictor=self.bht_entry, 
                pht_index_size=self.pc_index_size, 
                bht_index_size=self.bht_index_size, 
                min_index=self.pc_min_index)
        elif self.indexing_method == "PShare":
            return PSharePredictorWidget(
                self.predictor_frame, 
                index_size=self.pc_index_size, 
                predictor=self.bht_entry, 
                min_index=self.pc_min_index)


root = tk.Tk()
app = Application(master=root)
app.mainloop() # Triggers GUI