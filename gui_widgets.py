import tkinter as tk
from tkinter import ttk

class TableWidget(ttk.Frame):
    def __init__(self, parent, **options):
        self.column_names = options.pop("column_names")
        super().__init__(parent, **options)
        cols = [i for i in range(len(self.column_names))]
        self.index = 0

            
        self.table = ttk.Treeview(self, **options, columns=cols, show='headings')
        for col in cols:
            self.table.heading(col, text=self.column_names[col])
            self.table.column(col, minwidth=0, width=4*len(self.column_names[col])+80)
        
        self.table.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def add_row(self, entry):
        self.table.insert('', tk.END, id=self.index, values=entry, tags=("all"))
        self.table.yview_moveto(1)
        self.index += 1

    def set_row_at_index(self, index, entry):
        if self.table.exists(index):
            self.table.item(index, values=entry)
        else:
            self.add_row(entry)

    def set_focus(self, index):
        for i in range(self.index):
            self.table.item(i, tags='all')
        self.table.item(index, tags='focus')
        self.table.tag_configure('all', background='white')
        self.table.tag_configure('focus', background='#a8ccff')
        self.table.yview_moveto(index/self.index)

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

class ImageWidget(ttk.Frame):
    def __init__(self, parent, **options):
        image_path = options.pop("image_path")
        super().__init__(parent, **options)

        img = tk.PhotoImage(file=image_path)
        image_panel = tk.Label(self, image = img)
        image_panel.image = img
        image_panel.pack(side = "bottom", fill = "both", expand = "yes")

class DiscreteIntSpinbox(ttk.Frame):
    def __init__(self, parent, **options):
        max = options.pop("max")
        
        super().__init__(parent, **options)
                
        valid_values = [''] + [str(i) for i in range(1, max + 1)]

        self.spinbox = ttk.Spinbox(
            self,
            from_=1,
            to=max,
            values=[i for i in range(1, max + 1)],
            validate='key',
            validatecommand= (self.register(lambda val : val in valid_values), '%P'),
            wrap=True)
        self.spinbox.pack()

    def get(self):
        return self.spinbox.get()