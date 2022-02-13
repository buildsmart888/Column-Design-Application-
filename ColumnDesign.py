import tkinter as tk
from tkinter import ttk
from Frames import StartPage, RectangularColumn, CircularColumn


class ColumnDesign(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = ttk.Frame(self)
        container.grid()
        container.columnconfigure(0, weight=1)
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry("%dx%d" % (self.width, self.height))
        self.title("JD. Column")
        self.LARGE_FONT = ("Veranda", 12)
        self.frames = dict()

        for FrameClass in (StartPage, RectangularColumn, CircularColumn):
            frame = FrameClass(container, self)
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(StartPage)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()


try:
    root = ColumnDesign()
    root.mainloop()
except:
    import traceback

    traceback.print_exc()
    input("Press Enter to end...")
