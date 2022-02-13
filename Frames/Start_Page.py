from os import path
import sys
from tkinter import ttk
from tkinter import BOTTOM
from Frames.Rectangular_Column import RectangularColumn
from Frames.Circular_Column import CircularColumn
from PIL import Image, ImageTk


class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ttk.Label(self, text='JD Column', font=("Veranda", 30))
        label.pack(side="top")
        self.load_objects()

        button1 = ttk.Button(self, text='Rectangular Column Design', image=self.Rectangular_Column, compound=BOTTOM,
                             command=lambda: controller.show_frame(RectangularColumn))
        button1.pack(side="left", padx=100)
        button2 = ttk.Button(self, text='Circular Column Design', image=self.Circular_Column, compound=BOTTOM,
                             command=lambda: controller.show_frame(CircularColumn))
        button2.pack(side="right", padx=100)

    def load_objects(self):
        try:
            bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
            path_to_CircularColumn = path.join(bundle_dir, "Objects", "Circular_Column.JPG")

            self.Circular_Column_Image = Image.open(path_to_CircularColumn)
            self.Circular_Column_Image = self.Circular_Column_Image.resize((400, 275))
            self.Circular_Column = ImageTk.PhotoImage(self.Circular_Column_Image)

            path_to_RectangularColumn = path.join(bundle_dir, "Objects", "Rectangular_Column.JPG")
            self.Rectangular_Column_Image = Image.open(path_to_RectangularColumn)
            self.Rectangular_Column_Image = self.Rectangular_Column_Image.resize((400, 275))
            self.Rectangular_Column = ImageTk.PhotoImage(self.Rectangular_Column_Image)
        except IOError as error:
            print(error)
