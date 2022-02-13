# IMPORTS_______________________________________________________________________________________________________________
import tkinter as tk
from tkinter import ttk
import Frames
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import tkinter.messagebox
import numpy as np


class RectangularColumn(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ttk.Label(self, text='Rectangular Column Design', font=controller.LARGE_FONT)
        label.grid(row=0, pady=10, padx=10, columnspan=10)
        self.grid_columnconfigure(3, weight=1)

        # CREATE TABS___________________________________________________________________________________________________
        #tabControl = ttk.Notebook(self)

        #self.tab1 = ttk.Frame(tabControl)
        #tabControl.add(self.tab1, text='Uniaxial Bending')

        #self.tab2 = ttk.Frame(tabControl)
        #tabControl.add(self.tab2, text='Biaxial Bending')

        #tabControl.grid(column=0)

        button1 = ttk.Button(self, text='Back To Start Page',
                             command=lambda: controller.show_frame(Frames.StartPage))
        button1.grid(row=16, columnspan=10, pady=5)

        button2 = ttk.Button(self, text='Run', command=self.create_Pn_Mn_diagram)
        button2.grid(row=15, columnspan=10)

        button3 = ttk.Button(self, text='Preview Section', command=self.create_col_layout_diagram)
        button3.grid(row=13, column=4, columnspan=10, pady=60)

        # SET VARIABLES TO BE PULLED FROM GUI INTO CODE_________________________________________________________________
        self.b = tk.StringVar()  # Column Width
        self.fc = tk.StringVar()  # f'c
        self.cc = tk.StringVar()  # Clear Cover
        self.fy = tk.StringVar()  # Fy
        self.elast = tk.StringVar()  # Steel modulus of elasticity
        self.h = tk.StringVar()  # Height of the column
        self.phi_tie = tk.IntVar()  # Strength Reduction Factor for Tied Column
        self.phi_spiral = tk.IntVar()  # Strength Reduction Factor for Spiral Column
        self.pu = tk.StringVar()  # Axial demand
        self.mu = tk.StringVar()  # Moment demand
        self.ntopbot = tk.StringVar()  # Number of top and bottom face bars of column
        self.nside = tk.StringVar()  # Additional bars each side of column

        # CREATE DROP DOWN MENU'S_______________________________________________________________________________________
        self.rebar = ["#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11", "#14", "#18"]
        self.lBar = tk.StringVar(self)
        self.tBar = tk.StringVar(self)
        self.tBar.set(self.rebar[0])
        self.lBar.set(self.rebar[0])

        # CREATE LABELFRAME FOR COLUMN DIMENSIONS AND PROPERTIES ON GUI_________________________________________________
        self.labelframe = ttk.LabelFrame(self, text='Concrete Details')
        self.labelframe.grid(column=0, row=1, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe, text='Depth (along Y):').grid(column=0, row=2, sticky=tk.W, padx=5)
        tk.Label(self.labelframe, text='Width (along X):').grid(column=0, row=3, sticky=tk.W, padx=5)
        tk.Label(self.labelframe, text='Clear Cover:').grid(column=0, row=4, sticky=tk.W, padx=5)
        tk.Label(self.labelframe, text="Strength, f'c:").grid(column=0, row=5, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe, textvariable=self.b).grid(row=2, column=1)
        tk.Entry(self.labelframe, textvariable=self.h).grid(row=3, column=1)
        tk.Entry(self.labelframe, textvariable=self.cc).grid(row=4, column=1)
        tk.Entry(self.labelframe, textvariable=self.fc).grid(row=5, column=1)
        tk.Label(self.labelframe, text='in').grid(row=2, column=2, padx=5)  # Column Width
        tk.Label(self.labelframe, text='in').grid(row=3, column=2, padx=5)  # Column Height
        tk.Label(self.labelframe, text='in').grid(row=4, column=2, padx=5)  # Clear Cov er
        tk.Label(self.labelframe, text='psi').grid(row=5, column=2, padx=5)  # f'c

        self.labelframe1 = ttk.LabelFrame(self, text='Reinforcement Details')
        self.labelframe1.grid(column=0, row=5, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe1, text='Strength, fy:').grid(row=6, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text='Elasticity, Es:').grid(row=7, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text='Top/Bottom Face Bars:').grid(row=8, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text="Additional Bars Each Side:").grid(row=9, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text="Longitudinal Bar Size:").grid(row=10, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe1, text="Transverse Bar Size:").grid(row=11, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe1, textvariable=self.fy).grid(row=6, column=1, sticky=tk.W)
        tk.Entry(self.labelframe1, textvariable=self.elast).grid(row=7, column=1, sticky=tk.W)
        tk.Entry(self.labelframe1, textvariable=self.ntopbot).grid(row=8, column=1, sticky=tk.W)
        tk.Entry(self.labelframe1, textvariable=self.nside).grid(row=9, column=1, sticky=tk.W)
        tk.OptionMenu(self.labelframe1, self.lBar, *self.rebar).grid(row=10, column=1, sticky=tk.W)
        tk.OptionMenu(self.labelframe1, self.tBar, *self.rebar).grid(row=11, column=1, sticky=tk.W)
        tk.Label(self.labelframe1, text='psi').grid(row=6, column=2, padx=5, sticky=tk.W)  # Fy
        tk.Label(self.labelframe1, text='psi').grid(row=7, column=2, padx=5, sticky=tk.W)  # E

        self.labelframe2 = ttk.LabelFrame(self, text='Factored Demand')
        self.labelframe2.grid(column=0, row=11, sticky=tk.W, pady=10, padx=10)
        tk.Label(self.labelframe2, text='Axial, Pu:').grid(row=12, column=0, sticky=tk.W, padx=5)
        tk.Label(self.labelframe2, text='Moment, Mu:').grid(row=13, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.labelframe2, textvariable=self.pu).grid(row=12, column=1)
        tk.Entry(self.labelframe2, textvariable=self.mu).grid(row=13, column=1)
        tk.Label(self.labelframe2, text='kip').grid(row=12, column=2, padx=5)  # Pu
        tk.Label(self.labelframe2, text='kip-ft').grid(row=13, column=2, padx=5)  # Mu

        self.labelframe3 = ttk.LabelFrame(self, text='Confinement Details')
        self.labelframe3.grid(column=0, row=13, sticky=tk.W, pady=10, padx=10)
        tk.Checkbutton(self.labelframe3, text='Tied Reinforcement', variable=self.phi_tie).grid()
        tk.Checkbutton(self.labelframe3, text='Spiral Reinforcement', variable=self.phi_spiral).grid()

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
        fig1.subplots_adjust(0, 0, 1, 1)
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
        canvas = FigureCanvasTkAgg(fig1, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect('equal')

    # FUNCTION FOR CREATING COLUMN LAYOUT DIAGRAM_______________________________________________________________________

    def create_col_layout_diagram(self):

        # CHECK FOR INPUTS
        if not self.b.get():
            tk.messagebox.showinfo('Error', 'Please input the depth of the column.')
            return
        if not self.h.get():
            tk.messagebox.showinfo('Error', 'Please input the width of the column.')
            return
        if not self.cc.get():
            tk.messagebox.showinfo('Error', 'Please input clear cover dimension.')
            return
        if not self.ntopbot.get():
            tk.messagebox.showinfo('Error', 'Please input the number of top/bottom bars for the column.')
            return
        if not self.nside.get():
            tk.messagebox.showinfo('Error', 'Please input the number of side bars for the column.')
            return

        # GET CONSTANTS FROM GUI TO RUN IN CODE_________________________________________________________________________
        global DBAR, DBAR_T, PHI, DN
        CC = float(self.cc.get())  # clear cover
        B = float(self.b.get())  # vertical dimension of concrete column
        H = float(self.h.get())  # horizontal dimension of column
        NTOPBOT = int(self.ntopbot.get())
        NSIDE = int(self.nside.get())
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

        # DETERMINE COLUMN BAR POSITION ARRAY FOR GRAPHING______________________________________________________________
        xline1 = np.linspace((H / 2 - CC - DBAR_T - DBAR / 2), (-H / 2 + CC + DBAR_T + DBAR / 2), NTOPBOT)
        yline1 = np.array([B / 2 - CC - DBAR_T - DBAR / 2])
        xline1 = np.resize(xline1, (1, NTOPBOT))
        yline1 = np.resize(yline1, (1, NTOPBOT))

        xline3 = np.linspace((H / 2 - CC - DBAR_T - DBAR / 2), (-H / 2 + CC + DBAR_T + DBAR / 2), NTOPBOT)
        yline3 = np.array([-B / 2 + CC + DBAR_T + DBAR / 2])
        xline3 = np.resize(xline3, (1, NTOPBOT))
        yline3 = np.resize(yline3, (1, NTOPBOT))

        yline4 = np.linspace((B / 2 - CC - DBAR_T - DBAR / 2), (-B / 2 + CC + DBAR_T + DBAR / 2), NSIDE + 2)
        xline4 = np.array([-H / 2 + CC + DBAR_T + DBAR / 2])
        yline4 = np.resize(yline4, (1, NSIDE + 2))
        xline4 = np.resize(xline4, (1, NSIDE + 2))

        yline2 = np.linspace((B / 2 - CC - DBAR_T - DBAR / 2), (-B / 2 + CC + DBAR_T + DBAR / 2), NSIDE + 2)
        xline2 = np.array([H / 2 - CC - DBAR_T - DBAR / 2])
        yline2 = np.resize(yline2, (1, NSIDE + 2))
        xline2 = np.resize(xline2, (1, NSIDE + 2))

        # CHECK SPACING OF REINFORCEMENT
        hspacing = round((H - (2 * CC) - (2 * DBAR_T) - (NTOPBOT * DBAR)) / (NTOPBOT - 1),
                         2)  # Spacing of top/bottom bars
        vspacing = round((B - (2 * CC) - (2 * DBAR_T) - (2 * DBAR) - (NSIDE * DBAR)) / (NSIDE + 1),
                         2)  # Spacing of side bars

        if hspacing - DBAR <= 1 or hspacing - DBAR <= DBAR:
            tk.messagebox.showinfo('Error', 'Longitudinal Reinforcement is spaced to closely. '
                                            'Adjust column bar configuration.')
            return
        if vspacing - DBAR <= 1 or vspacing - DBAR <= DBAR:
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
        # Plot the points of the rectangular column
        ax1.set_xlim((-H / 2) - 10, (H / 2) + 10)
        ax1.set_ylim((-B / 2) - 10, (B / 2) + 10)
        ax1.hlines(B / 2, -H / 2, H / 2, colors='r')
        ax1.hlines(-B / 2, -H / 2, H / 2, colors='r')
        ax1.vlines(-H / 2, -B / 2, B / 2, colors='r')
        ax1.vlines(H / 2, -B / 2, B / 2, color='r')
        x1 = H / 2
        x2 = -H / 2
        y1 = -B / 2
        y2 = B / 2
        ax1.axvspan(x1, x2, ymin=0.5 - ((y1 / (y1 - 10)) / 2), ymax=0.5 + ((y2 / (y2 + 10)) / 2), color='gray')
        # Plot the bars on the column
        ax1.plot(xline1, yline1, 'o', color='red')
        ax1.plot(xline3, yline3, 'o', color='red')
        ax1.plot(xline4, yline4, 'o', color='red')
        ax1.plot(xline2, yline2, 'o', color='red')
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
        ax1.set_title(f"{self.b.get()} x {self.h.get()}''")
        # Plot the canvas on tkinter window
        canvas = FigureCanvasTkAgg(fig1, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect("equal")

    # FUNCTION FOR CREATING THE INTERACTION DIAGRAM_____________________________________________________________________

    def create_Pn_Mn_diagram(self):

        # CHECK FOR INPUTS
        if not self.b.get():
            tk.messagebox.showinfo('Error', 'Please input the depth of the column.')
            return
        if not self.h.get():
            tk.messagebox.showinfo('Error', 'Please input the width of the column.')
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
        if not self.elast.get():
            tk.messagebox.showinfo('Error', 'Please input modulus of elasticity of steel "E".')
            return
        if not self.ntopbot.get():
            tk.messagebox.showinfo('Error', 'Please input the number of top/bottom bars for the column.')
            return
        if not self.nside.get():
            tk.messagebox.showinfo('Error', 'Please input the number of side bars for the column.')
            return
        if (self.phi_spiral.get() == 1 and self.phi_tie.get() == 1) or (self.phi_spiral.get() == 0
                                                                        and self.phi_tie.get() == 0):
            tk.messagebox.showinfo('Error', 'Please choose either spiral or tied reinforcement.')
            return

        # GET CONSTANTS FROM GUI TO RUN IN CODE_________________________________________________________________________
        global DBAR, dn, AS
        global DBAR_T
        global PHI
        global DN
        FC = float(self.fc.get())  # concrete compressive strength
        CC = float(self.cc.get())  # clear cover
        B = float(self.b.get())  # vertical dimension of concrete column
        FY = float(self.fy.get())  # yield stress of longitudinal reinforcement
        ELAST = float(self.elast.get())  # modulus of elasticity of steel reinforcement
        H = float(self.h.get())  # horizontal dimension of column
        if not self.pu.get():
            PU = 0
        else:
            PU = float(self.pu.get())  # factored axial load demand
        if not self.mu.get():
            MU = 0
        else:
            MU = float(self.mu.get())  # factored moment demand
        NTOPBOT = int(self.ntopbot.get())
        NSIDE = int(self.nside.get())
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
        ETY = FY / ELAST

        # DETERMINE COLUMN BAR POSITION ARRAY FOR GRAPHING______________________________________________________________
        xline1 = np.linspace((H / 2 - CC - DBAR_T - DBAR / 2), (-H / 2 + CC + DBAR_T + DBAR / 2), NTOPBOT)
        yline1 = np.array([B / 2 - CC - DBAR_T - DBAR / 2])
        xline1 = np.resize(xline1, (1, NTOPBOT))
        yline1 = np.resize(yline1, (1, NTOPBOT))

        xline3 = np.linspace((H / 2 - CC - DBAR_T - DBAR / 2), (-H / 2 + CC + DBAR_T + DBAR / 2), NTOPBOT)
        yline3 = np.array([-B / 2 + CC + DBAR_T + DBAR / 2])
        xline3 = np.resize(xline3, (1, NTOPBOT))
        yline3 = np.resize(yline3, (1, NTOPBOT))

        yline4 = np.linspace((B / 2 - CC - DBAR_T - DBAR / 2), (-B / 2 + CC + DBAR_T + DBAR / 2), NSIDE + 2)
        xline4 = np.array([-H / 2 + CC + DBAR_T + DBAR / 2])
        yline4 = np.resize(yline4, (1, NSIDE + 2))
        xline4 = np.resize(xline4, (1, NSIDE + 2))

        yline2 = np.linspace((B / 2 - CC - DBAR_T - DBAR / 2), (-B / 2 + CC + DBAR_T + DBAR / 2), NSIDE + 2)
        xline2 = np.array([H / 2 - CC - DBAR_T - DBAR / 2])
        yline2 = np.resize(yline2, (1, NSIDE + 2))
        xline2 = np.resize(xline2, (1, NSIDE + 2))

        # DETERMINE COLUMN BAR (DN) POSITION ARRAY FOR CALCULATION______________________________________________________
        DN = []
        nbars = (NTOPBOT * 2) + (NSIDE * 2)
        hspacing = round((H - (2 * CC) - (2 * DBAR_T) - (NTOPBOT * DBAR)) / (NTOPBOT - 1),
                         2)  # Spacing of top/bottom bars
        vspacing = round((B - (2 * CC) - (2 * DBAR_T) - (2 * DBAR) - (NSIDE * DBAR)) / (NSIDE + 1),
                         2)  # Spacing of side bars

        for i in range(0, NSIDE * 2, 1):
            if i < NSIDE:
                dn = CC + DBAR_T + DBAR / 2
                DN.append(dn)
            else:
                dn = H - CC - DBAR_T - DBAR / 2
                DN.append(dn)

        for i in range(0, NTOPBOT, 1):
            if i == 0:
                dn = CC + DBAR_T + DBAR / 2
                DN.append(dn)
            else:
                dn = dn + hspacing
                DN.append(dn)

        for i in range(0, NTOPBOT, 1):
            if i == 0:
                dn = CC + DBAR_T + DBAR / 2
                DN.append(dn)
            else:
                dn = dn + hspacing
                DN.append(dn)

        # CHECK SPACING OF REINFORCEMENT
        if hspacing - DBAR <= 1 or hspacing - DBAR <= DBAR:
            tk.messagebox.showinfo('Error', 'Longitudinal Reinforcement is spaced to closely. '
                                            'Adjust column bar configuration.')
            return
        if vspacing - DBAR <= 1 or vspacing - DBAR <= DBAR:
            tk.messagebox.showinfo('Error', 'Longitudinal Reinforcement is spaced to closely. '
                                            'Adjust column bar configuration.')
            return

        # BEGIN LOOP OF "C" VARIABLE____________________________________________________________________________________
        Pn = []
        Mn = []
        for c in np.linspace(0.01, 5 * H, 7000):

            # CREATE ARRAY VARIABLES____________________________________________________________________________________
            a = []
            fs = []
            es = []
            PHI = []
            pn = []
            mn = []

            # CALCULATE WIDTH OF COMPRESSIVE STRESS BLOCK "A"___________________________________________________________
            if c * BETA1 <= H:
                A = (c * BETA1)
            else:
                A = H
            a.append(A)

            # CREATE STRAIN ARRAY_______________________________________________________________________________________
            for n in np.linspace(0, nbars - 1, nbars):
                # Create strain array
                Es = (0.003 / c) * (c - DN[int(n)])
                es.append(Es)

            # CALCULATE STRESS IN STEEL_________________________________________________________________________________
            ES = np.array(es)
            fs_1 = ES * ELAST
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
            if self.phi_spiral.get() == 1 and self.phi_tie.get() == 0:
                if abs(ets) <= ETY:
                    PHI = 0.75
                elif ETY < abs(ets) < 0.005:
                    PHI = 0.75 + 0.15 * ((abs(ets) - ETY) / (0.005 - ETY))
                else:
                    PHI = 0.9
            elif self.phi_tie.get() == 1 and self.phi_spiral.get() == 0:
                if abs(ets) <= ETY:
                    PHI = 0.65
                elif ETY < abs(ets) < 0.005:
                    PHI = 0.65 + 0.25 * ((abs(ets) - ETY) / (0.005 - ETY))
                else:
                    PHI = 0.9

            # CALCULATE PN AND MN FOR EACH BAR__________________________________________________________________________
            for n in np.linspace(0, nbars - 1, nbars):  # Number of longitudinal bars
                if A > DN[int(n)]:
                    PN = PHI * ((AS * (fs[int(n)] - 0.85 * FC)) / 1000)
                    pn.append(PN)
                    if DN[int(n)] < H / 2:
                        MN = (PHI * (AS * (fs[int(n)] - 0.85 * FC) * ((H / 2) - DN[int(n)]))) / 12000
                        mn.append(MN)
                    else:
                        MN = (PHI * (-(AS * (fs[int(n)] - 0.85 * FC) * (DN[int(n)] - (H / 2))))) / 12000
                        mn.append(MN)
                else:
                    PN = PHI * ((AS * fs[int(n)]) / 1000)
                    pn.append(PN)
                    if DN[int(n)] < H / 2:
                        MN = (PHI * (AS * fs[int(n)] * ((H / 2) - DN[int(n)]))) / 12000
                        mn.append(MN)
                    else:
                        MN = (PHI * (-(AS * fs[int(n)] * (DN[int(n)] - (H / 2))))) / 12000
                        mn.append(MN)
            Pnc = PHI * ((0.85 * FC * A * B) / 1000)
            Mnc = PHI * ((0.85 * FC * A * B * ((H / 2) - (A / 2))) / 12000)
            Pn.append((np.sum(pn)) + Pnc)
            Mn.append((np.sum(mn)) + Mnc)

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

        # PLOT THE COLUMN LAYOUT DIAGRAM________________________________________________________________________________
        fig1 = Figure(figsize=(3, 3), dpi=100, linewidth=5, edgecolor="#04253a")
        ax1 = fig1.add_subplot(111)
        # Add labelframe to canvas
        self.labelframe4 = ttk.LabelFrame(self, text='Section Preview')
        self.labelframe4.grid(column=4, row=1, rowspan=14, sticky=tk.W, padx=10)
        # Eliminate axes
        ax1.axis('off')
        # Display size of column
        ax1.set_title(f"{round(B)}''x {round(H)}''")
        # Plot the points of the rectangular column
        ax1.set_xlim((-H / 2) - 10, (H / 2) + 10)
        ax1.set_ylim((-B / 2) - 10, (B / 2) + 10)
        ax1.hlines(B / 2, -H / 2, H / 2, colors='r')
        ax1.hlines(-B / 2, -H / 2, H / 2, colors='r')
        ax1.vlines(-H / 2, -B / 2, B / 2, colors='r')
        ax1.vlines(H / 2, -B / 2, B / 2, color='r')
        x1 = H / 2
        x2 = -H / 2
        y1 = -B / 2
        y2 = B / 2
        ax1.axvspan(x1, x2, ymin=0.5 - ((y1 / (y1 - 10)) / 2), ymax=0.5 + ((y2 / (y2 + 10)) / 2), color='gray')
        # Plot the bars on the column
        ax1.plot(xline1, yline1, 'o', color='red')
        ax1.plot(xline3, yline3, 'o', color='red')
        ax1.plot(xline4, yline4, 'o', color='red')
        ax1.plot(xline2, yline2, 'o', color='red')
        # Plot the x-y directional arrows
        ax1.arrow(0.5, 0.5, 0.1, 0, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.arrow(0.5, 0.5, 0, 0.1, length_includes_head=True, head_width=0.015, head_length=0.02, color='black',
                  transform=fig1.transFigure)
        ax1.text(0.51, 0.61, 'y', transform=fig1.transFigure, fontsize=9)
        ax1.text(0.61, 0.51, 'x', transform=fig1.transFigure, fontsize=9)
        # Display size of column
        ax1.set_title(f"{self.b.get()} x {self.h.get()}''")
        # Plot the canvas on tkinter window
        canvas = FigureCanvasTkAgg(fig1, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=4, row=1, rowspan=14, padx=10)
        ax1.set_aspect('equal')
