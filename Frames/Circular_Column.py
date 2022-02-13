import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import tkinter.messagebox
import numpy as np
import math as m

import Frames


class CircularColumn(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.frames = None
        label = tk.Label(self, text='Circular Column Design', font=controller.LARGE_FONT)
        label.grid(row=0, pady=10, padx=10, columnspan=10)
        self.grid_columnconfigure(3, weight=1)

        button1 = ttk.Button(self, text='Back To Start Page', command=lambda: controller.show_frame(Frames.StartPage))
        button1.grid(row=16, columnspan=10, pady=5)

        button2 = ttk.Button(self, text='Run', command=self.create_Pn_Mn_diagram)
        button2.grid(row=15, columnspan=10)

        button3 = ttk.Button(self, text='Preview Section', command=self.create_col_layout_diagram)
        button3.grid(row=12, column=4, columnspan=10, pady=60)

        # SET VARIABLES TO BE PULLED FROM GUI INTO CODE_________________________________________________________________
        self.D = tk.StringVar()  # Column Diameter
        self.fc = tk.StringVar()  # f'c
        self.fy = tk.StringVar()  # Fy
        self.N = tk.StringVar()  # n
        self.Elast = tk.StringVar()  # Steel modulus of elasticity
        self.PHI_tie = tk.IntVar()  # Strength Reduction Factor for Tied Column
        self.PHI_spiral = tk.IntVar()  # Strength Reduction Factor for Spiral Column
        self.pu = tk.StringVar()  # Axial demand
        self.mu = tk.StringVar()  # Moment demand
        self.cc = tk.StringVar()  # Clear cover

        # CREATE DROP DOWN MENU'S_______________________________________________________________________________________
        self.rebar = ["#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11", "#14", "#18"]
        self.lBar = tk.StringVar()
        self.tBar = tk.StringVar()
        self.lBar.set(self.rebar[0])
        self.tBar.set(self.rebar[0])

        # CREATE LABELFRAME FOR COLUMN DIMENSIONS AND PROPERTIES ON GUI_________________________________________________
        self.labelframe = ttk.LabelFrame(self, text='Concrete Details')
        self.labelframe.grid(column=0, row=1, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe, text='Diameter:').grid(row=2, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe, text='Clear Cover:').grid(row=3, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe, text="Strength, f'c:").grid(row=4, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe, textvariable=self.D).grid(row=2, column=1)
        tk.Entry(self.labelframe, textvariable=self.cc).grid(row=3, column=1)
        tk.Entry(self.labelframe, textvariable=self.fc).grid(row=4, column=1)
        tk.Label(self.labelframe, text='in').grid(row=2, column=2, padx=5)  # Column Diameter
        tk.Label(self.labelframe, text='in').grid(row=3, column=2, padx=5)  # Clear Cover
        tk.Label(self.labelframe, text='psi').grid(row=4, column=2, padx=5)  # f'c

        self.labelframe1 = ttk.LabelFrame(self, text='Reinforcement Details')
        self.labelframe1.grid(column=0, row=4, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe1, text='Strength, fy:').grid(row=5, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text='Elasticity, Es:').grid(row=6, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text='Number of Longitudinal Bars:').grid(row=7, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text="Longitudinal Bar Size:").grid(row=8, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text="Transverse Bar Size:").grid(row=9, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe1, textvariable=self.fy).grid(row=5, column=1)
        tk.Entry(self.labelframe1, textvariable=self.Elast).grid(row=6, column=1)
        tk.Entry(self.labelframe1, textvariable=self.N).grid(row=7, column=1)
        tk.OptionMenu(self.labelframe1, self.lBar, *self.rebar).grid(row=8, column=1, sticky=tk.W)
        tk.OptionMenu(self.labelframe1, self.tBar, *self.rebar).grid(row=9, column=1, sticky=tk.W)
        tk.Label(self.labelframe1, text='psi').grid(row=5, column=2, padx=5)  # Fy
        tk.Label(self.labelframe1, text='psi').grid(row=6, column=2, padx=5)  # E

        self.labelframe2 = ttk.LabelFrame(self, text='Factored Demand')
        self.labelframe2.grid(column=0, row=9, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe2, text='Axial, Pu:').grid(row=10, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe2, text='Moment, Mu:').grid(row=11, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe2, textvariable=self.pu).grid(row=10, column=1)
        tk.Entry(self.labelframe2, textvariable=self.mu).grid(row=11, column=1)
        tk.Label(self.labelframe2, text='kip').grid(row=10, column=2, padx=5)  # Pu
        tk.Label(self.labelframe2, text='kip-ft').grid(row=11, column=2, padx=5)  # Mu

        self.labelframe3 = ttk.LabelFrame(self, text='Confinement Details')
        self.labelframe3.grid(column=0, row=12, sticky=tk.W, pady=10, padx=10)
        tk.Checkbutton(self.labelframe3, text='Tied Reinforcement', variable=self.PHI_tie).grid(row=13, column=0)
        tk.Checkbutton(self.labelframe3, text='Spiral Reinforcement', variable=self.PHI_spiral).grid(row=14, column=0)

        # DISPLAY CANVAS FOR INTERACTION DIAGRAM________________________________________________________________________
        fig = Figure(figsize=(6, 5), dpi=100, linewidth=5, edgecolor="#04253a")
        ax = fig.add_subplot(111)
        ax.grid()
        ax.set_ylabel('\u03A6Pn (kips)')
        ax.set_xlabel('\u03A6Mn (kip-ft)')
        ax.set_title("Interaction Diagram")
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=3, row=1, rowspan=14, padx=10, pady=10)

        # DISPLAY CANVAS FOR COLUMN LAYOUT DIAGRAM______________________________________________________________________
        fig1 = Figure(figsize=(3, 3), dpi=100, linewidth=5, edgecolor="#04253a")
        ax1 = fig1.add_subplot(111)
        # Add labelframe to canvas
        self.labelframe4 = ttk.LabelFrame(self, text='Section Preview')
        self.labelframe4.grid(column=4, row=1, rowspan=14, sticky=tk.W, padx=10)
        # Eliminate axes
        ax1.axis('off')
        # Plot the x-y directional arrows
        ax1.arrow(0.5, 0.5, 0.1, 0, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.arrow(0.5, 0.5, 0, 0.1, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.text(0.51, 0.61, 'y', transform=fig1.transFigure, fontsize=9)
        ax1.text(0.61, 0.51, 'x', transform=fig1.transFigure, fontsize=9)
        # Plot the canvas on tkinter window
        canvas = FigureCanvasTkAgg(fig1, self.labelframe4)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect('equal')

    # FUNCTION FOR CREATING COLUMN LAYOUT DIAGRAM_______________________________________________________________________

    def create_col_layout_diagram(self):

        # CHECK FOR INPUTS
        if not self.D.get():
            tk.messagebox.showinfo('Error', 'Please input diameter of column "D".')
            return
        if not self.cc.get():
            tk.messagebox.showinfo('Error', 'Please input clear cover dimension.')
            return
        if not self.N.get():
            tk.messagebox.showinfo('Error', 'Please input the number of longitudinal bars for the column "n".')
            return

        # GET CONSTANTS FROM GUI TO RUN IN CODE_________________________________________________________________________
        global PHI, DBAR, DBAR_T, theta1
        d = float(self.D.get())  # diameter of concrete column
        nbars = int(self.N.get())  # number of longitudinal bars
        CC = float(self.cc.get())  # clear cover
        LBAR = self.lBar.get()  # size of longitudinal reinforcement
        TBAR = self.tBar.get()  # size of transverse reinforcement

        # DETERMINE AREA AND DIAMETER OF LONGITUDINAL REBAR_____________________________________________________________
        if LBAR == "#3":
            DBAR = 0.375
        if LBAR == "#4":
            DBAR = 0.5
        if LBAR == "#5":
            DBAR = 0.625
        if LBAR == "6":
            DBAR = 0.75
        if LBAR == "#7":
            DBAR = 0.875
        if LBAR == "#8":
            DBAR = 1.0
        if LBAR == "#9":
            DBAR = 1.128
        if LBAR == "#10":
            DBAR = 1.27
        if LBAR == "#11":
            DBAR = 1.41
        if LBAR == "#14":
            DBAR = 1.693
        if LBAR == "#18":
            DBAR = 2.257

        # DETERMINE AREA AND DIAMETER OF TRANSVERSE REBAR_______________________________________________________________
        if TBAR == "#3":
            DBAR_T = 0.375
        if TBAR == "#4":
            DBAR_T = 0.5
        if TBAR == "#5":
            DBAR_T = 0.625
        if TBAR == "6":
            DBAR_T = 0.75
        if TBAR == "#7":
            DBAR_T = 0.875
        if TBAR == "#8":
            DBAR_T = 1.0
        if TBAR == "#9":
            DBAR_T = 1.128
        if TBAR == "#10":
            DBAR_T = 1.27
        if TBAR == "#11":
            DBAR_T = 1.41
        if TBAR == "#14":
            DBAR_T = 1.693
        if TBAR == "#18":
            DBAR_T = 2.257

        # DEFINE CONSTANTS______________________________________________________________________________________________
        x = []
        y = []

        # DETERMINE COLUMN BAR POSITION ARRAY FOR GRAPHING______________________________________________________________
        theta = (2 * m.pi / nbars)
        r = d / 2
        for i in np.linspace(0, nbars - 1, nbars):
            if i == 0:
                theta1 = 0
                X = (r - CC - DBAR_T - DBAR / 2) * m.cos(theta1)
                x.append(X)
                Y = (r - CC - DBAR_T - DBAR / 2) * m.sin(theta1)
                y.append(Y)
            else:
                theta1 = theta + theta1
                X = (r - CC - DBAR_T - DBAR / 2) * m.cos(theta1)
                x.append(X)
                Y = (r - CC - DBAR_T - DBAR / 2) * m.sin(theta1)
                y.append(Y)

        # CHECK SPACING OF REINFORCEMENT________________________________________________________________________________
        circumference = m.pi * d
        spacing = (circumference - (nbars * DBAR)) / nbars
        if spacing <= 1 or spacing <= DBAR:
            tk.messagebox.showinfo('Error', 'Longitudinal Reinforcement is spaced to closely. '
                                            'Adjust column bar configuration.')
            return

        # PLOT THE COLUMN LAYOUT DIAGRAM________________________________________________________________________________
        fig1 = Figure(figsize=(3, 3), dpi=100, linewidth=5, edgecolor="#04253a")
        ax1 = fig1.add_subplot(111)
        # Add labelframe to canvas
        self.labelframe4 = ttk.LabelFrame(self, text='Section Preview')
        self.labelframe4.grid(column=4, row=1, rowspan=14, sticky=tk.W, padx=10)
        # Eliminate axes
        ax1.axis('off')
        # Plot the x-y directional arrows
        ax1.arrow(0.5, 0.5, 0.1, 0, length_includes_head=True, head_width=0.015, head_length=0.02,
                  color='black',
                  transform=fig1.transFigure)
        ax1.arrow(0.5, 0.5, 0, 0.1, length_includes_head=True, head_width=0.015, head_length=0.02,
                  color='black',
                  transform=fig1.transFigure)
        ax1.text(0.51, 0.61, 'y', transform=fig1.transFigure, fontsize=9)
        ax1.text(0.61, 0.51, 'x', transform=fig1.transFigure, fontsize=9)
        # Display size of column
        ax1.set_title(f"{round(d)}''\u03A6")
        # Plot the circular column
        ax1.set_xlim(-25, 25)
        ax1.set_ylim(-25, 25)
        if d > 50:
            ax1.set_xlim(-50, 50)
            ax1.set_ylim(-50, 50)
        if d > 100:
            ax1.set_xlim(-75, 75)
            ax1.set_ylim(-75, 75)
        if d > 150:
            tk.messagebox.showinfo('Error', 'Column diameter size is not supported. Please design manually.')
            return
        circle = plt.Circle((0, 0), d / 2, color="gray", ec="red", zorder=0)
        ax1.add_artist(circle)
        # Plot the bars on the column
        ax1.scatter(x, y, marker='o', color='red', zorder=10)
        # Plot the canvas on tkinter window
        canvas = FigureCanvasTkAgg(fig1, self.labelframe4)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect('equal')

    # FUNCTION FOR CREATING THE INTERACTION DIAGRAM_____________________________________________________________________

    def create_Pn_Mn_diagram(self):

        # CHECK FOR INPUTS
        if not self.D.get():
            tk.messagebox.showinfo('Error', 'Please input diameter of column "D".')
            return
        if not self.cc.get():
            tk.messagebox.showinfo('Error', 'Please input clear cover dimension.')
            return
        if not self.fc.get():
            tk.messagebox.showinfo('Error', 'Please input compressive strength of concrete "fc".')
            return
        if not self.fy.get():
            tk.messagebox.showinfo('Error', 'Please input yield strength of reinforcement "Fy".')
            return
        if not self.Elast.get():
            tk.messagebox.showinfo('Error', 'Please input modulus of elasticity of steel "E".')
            return
        if not self.N.get():
            tk.messagebox.showinfo('Error', 'Please input the number of longitudinal bars for the column "n".')
            return
        if (self.PHI_spiral.get() == 1 and self.PHI_tie.get() == 1) or \
                (self.PHI_spiral.get() == 0 and self.PHI_tie.get() == 0):
            tk.messagebox.showinfo('Error', 'Please choose either spiral or tied reinforcement.')
            return

        # GET CONSTANTS FROM GUI TO RUN IN CODE_________________________________________________________________________
        global PHI, DBAR, A, Ac, x_bar, DBAR_T, theta1, AS
        FC = float(self.fc.get())  # concrete compressive strength
        d = float(self.D.get())  # diameter of concrete column
        FY = float(self.fy.get())  # yield stress of longitudinal reinforcement
        nbars = int(self.N.get())  # number of longitudinal bars
        E = float(self.Elast.get())  # modulus of elasticity of steel reinforcement
        CC = float(self.cc.get())  # clear cover
        if not self.pu.get():
            PU = 0
        else:
            PU = float(self.pu.get())  # factored axial load demand
        if not self.mu.get():
            MU = 0
        else:
            MU = float(self.mu.get())  # factored moment demand
        LBAR = self.lBar.get()  # size of longitudinal reinforcement
        TBAR = self.tBar.get()  # size of transverse reinforcement

        # DETERMINE AREA AND DIAMETER OF LONGITUDINAL REBAR_____________________________________________________________
        if LBAR == "#3":
            AS = 0.11
            DBAR = 0.375
        if LBAR == "#4":
            AS = 0.20
            DBAR = 0.5
        if LBAR == "#5":
            AS = 0.31
            DBAR = 0.625
        if LBAR == "6":
            AS = 0.44
            DBAR = 0.75
        if LBAR == "#7":
            AS = 0.60
            DBAR = 0.875
        if LBAR == "#8":
            AS = 0.79
            DBAR = 1.0
        if LBAR == "#9":
            AS = 1.0
            DBAR = 1.128
        if LBAR == "#10":
            AS = 1.27
            DBAR = 1.27
        if LBAR == "#11":
            AS = 1.56
            DBAR = 1.41
        if LBAR == "#14":
            AS = 2.25
            DBAR = 1.693
        if LBAR == "#18":
            AS = 4
            DBAR = 2.257

        # DETERMINE AREA AND DIAMETER OF TRANSVERSE REBAR_______________________________________________________________
        if TBAR == "#3":
            DBAR_T = 0.375
        if TBAR == "#4":
            DBAR_T = 0.5
        if TBAR == "#5":
            DBAR_T = 0.625
        if TBAR == "6":
            DBAR_T = 0.75
        if TBAR == "#7":
            DBAR_T = 0.875
        if TBAR == "#8":
            DBAR_T = 1.0
        if TBAR == "#9":
            DBAR_T = 1.128
        if TBAR == "#10":
            DBAR_T = 1.27
        if TBAR == "#11":
            DBAR_T = 1.41
        if TBAR == "#14":
            DBAR_T = 1.693
        if TBAR == "#18":
            DBAR_T = 2.257

        # DETERMINE COMPRESSIVE STRESS DISTRIBUTION FACTOR "BETA1"______________________________________________________
        if 2500 <= FC <= 4000:
            BETA1 = 0.85
        elif 4000 < FC < 8000:
            BETA1 = 0.85 - ((0.05 * (FC - 4000)) / 1000)
        else:
            BETA1 = 0.65

        # DEFINE CONSTANTS______________________________________________________________________________________________
        ETY = FY / E
        Pn = []
        Mn = []
        x = []
        y = []

        # DETERMINE COLUMN BAR POSITION ARRAY FOR GRAPHING______________________________________________________________
        theta = (2 * m.pi / nbars)
        r = d / 2
        for i in np.linspace(0, nbars - 1, nbars):
            if i == 0:
                theta1 = 0
                X = (r - CC - DBAR_T - DBAR / 2) * m.cos(theta1)
                x.append(X)
                Y = (r - CC - DBAR_T - DBAR / 2) * m.sin(theta1)
                y.append(Y)
            else:
                theta1 = theta + theta1
                X = (r - CC - DBAR_T - DBAR / 2) * m.cos(theta1)
                x.append(X)
                Y = (r - CC - DBAR_T - DBAR / 2) * m.sin(theta1)
                y.append(Y)

        # DETERMINE COLUMN BAR (DN) POSITION ARRAY FOR CALCULATION______________________________________________________
        DN = x

        # CHECK SPACING OF REINFORCEMENT
        circumference = m.pi * d
        spacing = (circumference - (nbars * DBAR)) / nbars
        if spacing <= 1 or spacing <= DBAR:
            tk.messagebox.showinfo('Error', 'Longitudinal Reinforcement is spaced to closely. '
                                            'Adjust column bar configuration.')
            return

        # BEGIN LOOP OF "Theta" VARIABLE________________________________________________________________________________
        for theta in np.linspace(0.01, m.pi, 5000):

            # CREATE ARRAY VARIABLES____________________________________________________________________________________
            a = []
            fs = []
            es = []
            PHI = []
            pn = []
            mn = []

            # CALCULATE WIDTH OF COMPRESSIVE STRESS BLOCK "A"___________________________________________________________
            if (d / 2) * (1 - (m.cos(theta))) <= d:
                A = (d / 2) * (1 - m.cos(theta))
            else:
                A = d
            a.append(A)

            # CREATE STRAIN ARRAY_______________________________________________________________________________________
            for n in np.linspace(0, nbars - 1, nbars):
                c = A / BETA1
                Es = (0.003 / c) * (c - DN[int(n)])
                es.append(Es)

            # CALCULATE STRESS IN STEEL_________________________________________________________________________________
            ES = np.array(es)
            fs_1 = ES * E
            for item in fs_1:
                if item < -FY:
                    item = -FY
                    fs.append(item)
                elif item > FY:
                    item = FY
                    fs.append(item)
                else:
                    fs.append(item)

            # DETERMINE PHI VALUE_______________________________________________________________________________________
            index_max = np.argmax(DN)
            ets = ES[int(index_max)]
            if self.PHI_spiral.get() == 1 and self.PHI_tie.get() == 0:
                if abs(ets) <= ETY:
                    PHI = 0.75
                elif ETY < abs(ets) < 0.005:
                    PHI = 0.75 + 0.15 * ((abs(ets) - ETY) / (0.005 - ETY))
                else:
                    PHI = 0.9
            elif self.PHI_tie.get() == 1 and self.PHI_spiral.get() == 0:
                if abs(ets) <= ETY:
                    PHI = 0.65
                elif ETY < abs(ets) < 0.005:
                    PHI = 0.65 + 0.25 * ((abs(ets) - ETY) / (0.005 - ETY))
                else:
                    PHI = 0.9
            if (self.PHI_spiral.get() == 1 and self.PHI_tie.get() == 1) or (self.PHI_spiral.get() == 0 and
                                                                            self.PHI_tie.get() == 0):
                tk.messagebox.showinfo('Error', 'Please choose either spiral or tied reinforcement.')
                return

            # CALCULATE PN AND MN FOR EACH BAR__________________________________________________________________________
            for n in np.linspace(0, nbars - 1, nbars):  # Number of longitudinal bars
                Ac = ((d / 2) ** 2) * (theta - ((m.sin(2 * theta)) / 2))
                x_bar = (2 * (d / 2) * (m.sin(theta)) ** 3) / (3 * (theta - ((m.sin(2 * theta)) / 2)))
                if A > DN[int(n)]:
                    PN = PHI * (AS * (fs[int(n)] - 0.85 * FC)) / 1000
                    pn.append(PN)
                    if DN[int(n)] < d / 2:
                        MN = (PHI * (AS * (fs[int(n)] - 0.85 * FC) * ((d / 2) - DN[int(n)]))) / 12000
                        mn.append(MN)
                    else:
                        MN = (PHI * (-(AS * (fs[int(n)] - 0.85 * FC) * (DN[int(n)] - (d / 2))))) / 12000
                        mn.append(MN)
                else:
                    PN = PHI * ((AS * fs[int(n)]) / 1000)
                    pn.append(PN)
                    if DN[int(n)] < d / 2:
                        MN = (PHI * (AS * fs[int(n)] * ((d / 2) - DN[int(n)]))) / 12000
                        mn.append(MN)
                    else:
                        MN = (PHI * (-(AS * fs[int(n)] * (DN[int(n)] - (d / 2))))) / 12000
                        mn.append(MN)
            Pnc = PHI * ((0.85 * FC * Ac) / 1000)
            Mnc = PHI * ((0.85 * FC * Ac * x_bar) / 12000)
            Pn.append(np.sum(pn) + Pnc)
            Mn.append(np.sum(mn) + Mnc)

        # PLOT THE INTERACTION DIAGRAM__________________________________________________________________________________
        Pn = np.asarray(Pn)
        Mn = np.asarray(Mn)
        fig = Figure(figsize=(6, 5), dpi=100, linewidth=5, edgecolor="#04253a")
        ax = fig.add_subplot(111)
        ax.plot(Mn, Pn)
        ax.plot([min(Mn), max(Mn)], [0.8 * max(Pn), 0.8 * max(Pn)])
        ax.scatter(MU, PU, s=50, marker='x')
        ax.grid()
        ax.set_ylabel('\u03A6Pn (kips)')
        ax.set_xlabel('\u03A6Mn (kip-ft)')
        ax.set_title("Interaction Diagram")
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=3, row=1, rowspan=14, padx=10)
        fig.tight_layout()

        # PLOT THE COLUMN LAYOUT DIAGRAM____________________________________________________________________________
        fig1 = Figure(figsize=(3, 3), dpi=100, linewidth=5, edgecolor="#04253a")
        ax1 = fig1.add_subplot(111)
        # Add labelframe to canvas
        self.labelframe4 = ttk.LabelFrame(self, text='Section Preview')
        self.labelframe4.grid(column=4, row=1, rowspan=14, sticky=tk.W, padx=10)
        # Eliminate axes
        ax1.axis('off')
        # Plot the x-y directional arrows
        ax1.arrow(0.5, 0.5, 0.1, 0, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.arrow(0.5, 0.5, 0, 0.1, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.text(0.51, 0.61, 'y', transform=fig1.transFigure, fontsize=9)
        ax1.text(0.61, 0.51, 'x', transform=fig1.transFigure, fontsize=9)
        # Display size of column
        ax1.set_title(f"{round(d)}''\u03A6")
        # Plot the circular column
        ax1.set_xlim(-25, 25)
        ax1.set_ylim(-25, 25)
        if d > 50:
            ax1.set_xlim(-50, 50)
            ax1.set_ylim(-50, 50)
        if d > 100:
            ax1.set_xlim(-75, 75)
            ax1.set_ylim(-75, 75)
        if d > 150:
            tk.messagebox.showinfo('Error', 'Column diameter size is not supported. Please design manually.')
            return
        circle = plt.Circle((0, 0), d / 2, color="gray", ec="red", zorder=0)
        ax1.add_artist(circle)
        # Plot the bars on the column
        ax1.scatter(x, y, marker='o', color='red', zorder=10)
        # Plot the canvas on tkinter window
        canvas = FigureCanvasTkAgg(fig1, self.labelframe4)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect('equal')
