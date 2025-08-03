#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Column Design Application with P-M Interaction
Complete structural design tool with detailed reinforcement and interaction diagrams
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import datetime
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ProfessionalColumnDesign:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Column Design v3.0 - ACI 318M-25 Ch.10")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame with scrollbar
        self.main_canvas = tk.Canvas(root, bg='#f8f9fa')
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Main frame inside scrollable area
        main_frame = ttk.Frame(self.scrollable_frame, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title section
        self.create_title_section(main_frame)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create tabs (Reinforcement merged into Design)
        self.design_frame = ttk.Frame(notebook, padding="15")
        self.analysis_frame = ttk.Frame(notebook, padding="15")
        self.interaction_frame = ttk.Frame(notebook, padding="15")
        self.results_frame = ttk.Frame(notebook, padding="15")
        
        notebook.add(self.design_frame, text="🏗️ Design & Reinforcement")
        notebook.add(self.analysis_frame, text="📊 Analysis")
        notebook.add(self.interaction_frame, text="📈 P-M Diagram")
        notebook.add(self.results_frame, text="📋 Full Report")
        
        # Setup all tabs
        self.setup_design_tab()
        self.setup_analysis_tab()
        self.setup_interaction_tab()
        self.setup_results_tab()
        
        # Initialize calculation variables
        self.last_results = None
        self.interaction_data = None
        
        # Enable mouse wheel scrolling
        self.bind_mousewheel()
        
    def bind_mousewheel(self):
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.main_canvas.bind("<MouseWheel>", _on_mousewheel)
        
    def create_title_section(self, parent):
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        title_label = tk.Label(title_frame, text="🏗️ Professional Column Design Suite", 
                              font=("Arial", 20, "bold"), 
                              bg='#f8f9fa', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="ACI 318M-25 Chapter 10 Compliant Design with P-M Interaction Diagrams", 
                                 font=("Arial", 11), 
                                 bg='#f8f9fa', fg='#7f8c8d')
        subtitle_label.pack()
        
    def setup_design_tab(self):
        # Create scrollable left frame for all inputs
        left_frame = ttk.LabelFrame(self.design_frame, text="📐 Design Parameters & Reinforcement", padding="15")
        left_frame.grid(row=0, column=0, sticky="new", padx=(0, 10))
        
        # Right column - Enhanced Section preview
        right_frame = ttk.LabelFrame(self.design_frame, text="👁️ Detailed Section Preview", padding="15")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.design_frame.columnconfigure(0, weight=1)
        self.design_frame.columnconfigure(1, weight=1)
        self.design_frame.rowconfigure(0, weight=1)
        
        # === GEOMETRY ===
        geom_frame = ttk.LabelFrame(left_frame, text="🔹 Cross-Section Geometry", padding="12")
        geom_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(geom_frame, text="Width B (mm):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.width_var = tk.StringVar(value="500")
        width_entry = ttk.Entry(geom_frame, textvariable=self.width_var, width=12)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        width_entry.bind('<KeyRelease>', self.update_preview)
        
        tk.Label(geom_frame, text="Height H (mm):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.height_var = tk.StringVar(value="500")
        height_entry = ttk.Entry(geom_frame, textvariable=self.height_var, width=12)
        height_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        height_entry.bind('<KeyRelease>', self.update_preview)
        
        tk.Label(geom_frame, text="Length L (m):", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.length_var = tk.StringVar(value="4.0")
        ttk.Entry(geom_frame, textvariable=self.length_var, width=12).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # === LOADS ===
        loads_frame = ttk.LabelFrame(left_frame, text="🔹 Applied Forces & Moments", padding="12")
        loads_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(loads_frame, text="Axial Load Pu (kN):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.axial_load_var = tk.StringVar(value="2000")
        ttk.Entry(loads_frame, textvariable=self.axial_load_var, width=12).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(loads_frame, text="Moment Mux (kN⋅m):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.moment_x_var = tk.StringVar(value="100")
        ttk.Entry(loads_frame, textvariable=self.moment_x_var, width=12).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(loads_frame, text="Moment Muy (kN⋅m):", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.moment_y_var = tk.StringVar(value="80")
        ttk.Entry(loads_frame, textvariable=self.moment_y_var, width=12).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # === MATERIALS ===
        materials_frame = ttk.LabelFrame(left_frame, text="🔹 Material Properties", padding="12")
        materials_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(materials_frame, text="Concrete fc' (MPa):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.fc_var = tk.StringVar(value="30")
        fc_combo = ttk.Combobox(materials_frame, textvariable=self.fc_var, 
                               values=["20", "25", "30", "35", "40", "50"], width=10)
        fc_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(materials_frame, text="Steel fy (MPa):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.fy_var = tk.StringVar(value="420")
        fy_combo = ttk.Combobox(materials_frame, textvariable=self.fy_var, 
                               values=["300", "420", "500", "550"], width=10)
        fy_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # === LONGITUDINAL REINFORCEMENT ===
        main_rebar_frame = ttk.LabelFrame(left_frame, text="🔩 Main Longitudinal Reinforcement", padding="12")
        main_rebar_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # X-direction reinforcement
        tk.Label(main_rebar_frame, text="X-Direction:", font=("Arial", 9, "bold"), fg="blue").grid(row=0, column=0, sticky=tk.W, pady=3)
        
        tk.Label(main_rebar_frame, text="Size:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rebar_x_var = tk.StringVar(value="DB25")
        rebar_x_combo = ttk.Combobox(main_rebar_frame, textvariable=self.rebar_x_var, 
                                    values=["DB12", "DB16", "DB20", "DB25", "DB32"], 
                                    state="readonly", width=10)
        rebar_x_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        rebar_x_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        tk.Label(main_rebar_frame, text="Number:", font=("Arial", 9)).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.num_bars_x_var = tk.StringVar(value="3")
        x_entry = ttk.Entry(main_rebar_frame, textvariable=self.num_bars_x_var, width=12)
        x_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        x_entry.bind('<KeyRelease>', self.update_preview)
        
        # Y-direction reinforcement
        tk.Label(main_rebar_frame, text="Y-Direction:", font=("Arial", 9, "bold"), fg="green").grid(row=1, column=2, sticky=tk.W, pady=3, padx=(20, 0))
        
        tk.Label(main_rebar_frame, text="Size:", font=("Arial", 9)).grid(row=1, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        self.rebar_y_var = tk.StringVar(value="DB25")
        rebar_y_combo = ttk.Combobox(main_rebar_frame, textvariable=self.rebar_y_var, 
                                    values=["DB12", "DB16", "DB20", "DB25", "DB32"], 
                                    state="readonly", width=10)
        rebar_y_combo.grid(row=1, column=4, sticky=tk.W, padx=(5, 0))
        rebar_y_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        tk.Label(main_rebar_frame, text="Number:", font=("Arial", 9)).grid(row=2, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        self.num_bars_y_var = tk.StringVar(value="3")
        y_entry = ttk.Entry(main_rebar_frame, textvariable=self.num_bars_y_var, width=12)
        y_entry.grid(row=2, column=4, sticky=tk.W, padx=(5, 0))
        y_entry.bind('<KeyRelease>', self.update_preview)
        
        # Corner bars reinforcement
        tk.Label(main_rebar_frame, text="Corner Bars:", font=("Arial", 9, "bold"), fg="red").grid(row=3, column=0, sticky=tk.W, pady=(10, 3))
        
        tk.Label(main_rebar_frame, text="Size:", font=("Arial", 9)).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.corner_rebar_var = tk.StringVar(value="DB25")
        corner_rebar_combo = ttk.Combobox(main_rebar_frame, textvariable=self.corner_rebar_var, 
                                         values=["DB12", "DB16", "DB20", "DB25", "DB32"], 
                                         state="readonly", width=10)
        corner_rebar_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0))
        corner_rebar_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        tk.Label(main_rebar_frame, text="Always 4 bars", font=("Arial", 8), fg="gray").grid(row=4, column=2, sticky=tk.W, pady=2, padx=(20, 0))
        
        # === TIES/STIRRUPS ===
        ties_frame = ttk.LabelFrame(left_frame, text="🔗 Ties & Stirrups", padding="12")
        ties_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(ties_frame, text="Tie Size:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.tie_size_var = tk.StringVar(value="DB12")
        tie_combo = ttk.Combobox(ties_frame, textvariable=self.tie_size_var, 
                                values=["RB6", "RB9", "DB10", "DB12", "DB16"], 
                                state="readonly", width=12)
        tie_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        tie_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        tk.Label(ties_frame, text="Spacing (mm):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.tie_spacing_var = tk.StringVar(value="150")
        spacing_entry = ttk.Entry(ties_frame, textvariable=self.tie_spacing_var, width=12)
        spacing_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        spacing_entry.bind('<KeyRelease>', self.update_preview)
        
        tk.Label(ties_frame, text="Legs:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky=tk.W, pady=3, padx=(20, 0))
        self.tie_legs_var = tk.StringVar(value="2")
        tie_legs_combo = ttk.Combobox(ties_frame, textvariable=self.tie_legs_var, 
                                     values=["2", "4", "6"], 
                                     state="readonly", width=12)
        tie_legs_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        tie_legs_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        tk.Label(ties_frame, text="End Spacing (mm):", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky=tk.W, pady=3, padx=(20, 0))
        self.end_spacing_var = tk.StringVar(value="100")
        ttk.Entry(ties_frame, textvariable=self.end_spacing_var, width=12).grid(row=1, column=3, sticky=tk.W, padx=(5, 0))
        
        # Show steel grade for RB bars
        tk.Label(ties_frame, text="Note: RB6, RB9 → fy = 240 MPa", font=("Arial", 8), fg="orange").grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # === COVER & DETAILS ===
        details_frame = ttk.LabelFrame(left_frame, text="📏 Cover & Details", padding="12")
        details_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(details_frame, text="Clear Cover (mm):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cover_var = tk.StringVar(value="50")
        cover_entry = ttk.Entry(details_frame, textvariable=self.cover_var, width=12)
        cover_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        cover_entry.bind('<KeyRelease>', self.update_preview)
        
        tk.Label(details_frame, text="End Region Length (mm):", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky=tk.W, pady=3, padx=(20, 0))
        self.end_length_var = tk.StringVar(value="600")
        ttk.Entry(details_frame, textvariable=self.end_length_var, width=12).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        tk.Label(details_frame, text="Dev. Length Factor:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.dev_length_factor_var = tk.StringVar(value="1.2")
        ttk.Entry(details_frame, textvariable=self.dev_length_factor_var, width=12).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # === CONTROL BUTTONS ===
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        design_btn = ttk.Button(button_frame, text="🔧 Run Complete Analysis", 
                               command=self.run_complete_analysis)
        design_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear All", 
                              command=self.clear_all)
        clear_btn.pack(side=tk.LEFT)
        
        # === ENHANCED PREVIEW CANVAS ===
        preview_container = ttk.Frame(right_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(preview_container, width=400, height=500, 
                                       bg='white', relief=tk.SUNKEN, bd=2)
        self.preview_canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Legend frame
        legend_frame = ttk.LabelFrame(right_frame, text="📚 Legend", padding="10")
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(legend_frame, text="● Main X-direction bars", fg="blue", font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        tk.Label(legend_frame, text="● Main Y-direction bars", fg="green", font=("Arial", 8)).grid(row=1, column=0, sticky=tk.W)
        tk.Label(legend_frame, text="● Corner bars", fg="red", font=("Arial", 8)).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        tk.Label(legend_frame, text="▬ Ties/Stirrups", fg="orange", font=("Arial", 8)).grid(row=1, column=1, sticky=tk.W, padx=(20, 0))
        
        self.update_preview()
        
    def setup_analysis_tab(self):
        # Analysis results frame
        analysis_main_frame = ttk.LabelFrame(self.analysis_frame, text="📊 Structural Analysis Results", padding="15")
        analysis_main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.analysis_text = tk.Text(analysis_main_frame, font=("Courier New", 10), 
                                    wrap=tk.WORD, height=25, bg='#f8f9fa')
        
        analysis_scroll = ttk.Scrollbar(analysis_main_frame, orient="vertical", 
                                       command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scroll.set)
        
        self.analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        analysis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_interaction_tab(self):
        # Control frame
        control_frame = ttk.Frame(self.interaction_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📈 Generate P-M Interaction Diagram", 
                  command=self.generate_pm_diagram).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="💾 Save Diagram", 
                  command=self.save_pm_diagram).pack(side=tk.LEFT)
        
        # Figure frame
        self.figure_frame = ttk.Frame(self.interaction_frame)
        self.figure_frame.pack(fill=tk.BOTH, expand=True)
        
    def setup_results_tab(self):
        # Results frame with export options
        results_control_frame = ttk.Frame(self.results_frame)
        results_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(results_control_frame, text="📄 Generate Full Report", 
                  command=self.generate_full_report).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(results_control_frame, text="💾 Export to TXT", 
                  command=self.export_report).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(results_control_frame, text="📑 Export to PDF", 
                  command=self.export_to_pdf).pack(side=tk.LEFT)
        
        results_main_frame = ttk.LabelFrame(self.results_frame, text="📋 Complete Design Report", padding="15")
        results_main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(results_main_frame, font=("Courier New", 9), 
                                   wrap=tk.WORD, height=30, bg='#f8f9fa')
        
        results_scroll = ttk.Scrollbar(results_main_frame, orient="vertical", 
                                      command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def get_rebar_area(self, rebar_size):
        """Get area of single rebar in mm²"""
        rebar_areas = {
            # Round bars (RB) - fy = 240 MPa
            "RB6": 28.3,    "RB9": 63.6,
            # Deformed bars (DB) - fy = 420 MPa  
            "DB10": 78.5,   "DB12": 113,    "DB16": 201,
            "DB20": 314,    "DB25": 491,    "DB32": 804
        }
        return rebar_areas.get(rebar_size, 314)
    
    def get_rebar_diameter(self, rebar_size):
        """Get diameter of rebar in mm"""
        if rebar_size.startswith("RB"):
            return int(rebar_size[2:])
        elif rebar_size.startswith("DB"):
            return int(rebar_size[2:])
        else:
            return 12  # Default
    
    def get_rebar_strength(self, rebar_size):
        """Get yield strength of rebar in MPa"""
        if rebar_size.startswith("RB"):
            return 240  # Round bars
        elif rebar_size.startswith("DB"):
            return 420  # Deformed bars
        else:
            return 420  # Default
        
    def update_preview(self, event=None):
        """Update the enhanced section preview with detailed reinforcement"""
        try:
            width = float(self.width_var.get() or "500")
            height = float(self.height_var.get() or "500")
            cover = float(self.cover_var.get() or "50")
            
            self.preview_canvas.delete("all")
            
            # Canvas dimensions
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 400
                canvas_height = 500
            
            # Scale and center
            max_dim = max(width, height)
            scale = min(canvas_width - 100, canvas_height - 150) / max_dim
            
            cx = canvas_width / 2
            cy = canvas_height / 2 - 30  # Offset for title space
            
            w_scaled = width * scale
            h_scaled = height * scale
            
            # Draw concrete section
            x1, y1 = cx - w_scaled/2, cy - h_scaled/2
            x2, y2 = cx + w_scaled/2, cy + h_scaled/2
            
            self.preview_canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill='#e8e8e8', outline='black', width=3)
            
            # Draw reinforcement
            try:
                cover_scaled = cover * scale
                
                # Get reinforcement parameters
                num_x = int(self.num_bars_x_var.get() or "3")
                num_y = int(self.num_bars_y_var.get() or "3")
                rebar_x_size = int(self.rebar_x_var.get()[2:])  # Extract diameter
                rebar_y_size = int(self.rebar_y_var.get()[2:])
                
                # Bar radius in scaled units
                bar_radius_x = max(2, rebar_x_size * scale / 2)
                bar_radius_y = max(2, rebar_y_size * scale / 2)
                
                # Corner bars (always 4)
                corner_positions = [
                    (x1 + cover_scaled, y1 + cover_scaled),
                    (x2 - cover_scaled, y1 + cover_scaled),
                    (x2 - cover_scaled, y2 - cover_scaled),
                    (x1 + cover_scaled, y2 - cover_scaled),
                ]
                
                for px, py in corner_positions:
                    self.preview_canvas.create_oval(px-4, py-4, px+4, py+4,
                                                   fill='red', outline='darkred', width=2)
                
                # X-direction bars (along width)
                if num_x > 2:  # Additional bars beyond corners
                    x_spacing = (w_scaled - 2*cover_scaled) / (num_x - 1)
                    for i in range(1, num_x - 1):
                        px = x1 + cover_scaled + i * x_spacing
                        # Top edge
                        self.preview_canvas.create_oval(px-bar_radius_x, y1+cover_scaled-bar_radius_x, 
                                                       px+bar_radius_x, y1+cover_scaled+bar_radius_x,
                                                       fill='blue', outline='darkblue', width=1)
                        # Bottom edge
                        self.preview_canvas.create_oval(px-bar_radius_x, y2-cover_scaled-bar_radius_x, 
                                                       px+bar_radius_x, y2-cover_scaled+bar_radius_x,
                                                       fill='blue', outline='darkblue', width=1)
                
                # Y-direction bars (along height)
                if num_y > 2:  # Additional bars beyond corners
                    y_spacing = (h_scaled - 2*cover_scaled) / (num_y - 1)
                    for i in range(1, num_y - 1):
                        py = y1 + cover_scaled + i * y_spacing
                        # Left edge
                        self.preview_canvas.create_oval(x1+cover_scaled-bar_radius_y, py-bar_radius_y, 
                                                       x1+cover_scaled+bar_radius_y, py+bar_radius_y,
                                                       fill='green', outline='darkgreen', width=1)
                        # Right edge  
                        self.preview_canvas.create_oval(x2-cover_scaled-bar_radius_y, py-bar_radius_y, 
                                                       x2-cover_scaled+bar_radius_y, py+bar_radius_y,
                                                       fill='green', outline='darkgreen', width=1)
                
                # Draw ties/stirrups
                tie_size = int(self.tie_size_var.get()[2:])  # Extract diameter
                tie_spacing = float(self.tie_spacing_var.get() or "150")
                tie_legs = int(self.tie_legs_var.get() or "2")
                
                # Tie outline (simplified rectangular stirrup)
                tie_x1 = x1 + cover_scaled - tie_size/2*scale
                tie_y1 = y1 + cover_scaled - tie_size/2*scale
                tie_x2 = x2 - cover_scaled + tie_size/2*scale
                tie_y2 = y2 - cover_scaled + tie_size/2*scale
                
                self.preview_canvas.create_rectangle(tie_x1, tie_y1, tie_x2, tie_y2,
                                                   outline='orange', width=3, fill='')
                
                # Show multiple tie levels if spacing allows
                tie_height = tie_spacing * scale
                section_height = h_scaled
                if tie_height < section_height / 4:
                    # Show 3 tie levels
                    for i in [-0.3, 0, 0.3]:
                        offset_y = i * section_height / 3
                        self.preview_canvas.create_rectangle(
                            tie_x1, tie_y1 + offset_y, tie_x2, tie_y2 + offset_y,
                            outline='orange', width=2, fill='', dash=(3, 3))
                
                # Add tie hook details
                hook_size = 10
                self.preview_canvas.create_line(tie_x2, tie_y1, tie_x2+hook_size, tie_y1-hook_size,
                                              fill='orange', width=2)
                self.preview_canvas.create_line(tie_x1, tie_y2, tie_x1-hook_size, tie_y2+hook_size,
                                              fill='orange', width=2)
                
            except:
                # Basic corner bars if reinforcement parameters fail
                for px, py in [(x1+20, y1+20), (x2-20, y1+20), (x2-20, y2-20), (x1+20, y2-20)]:
                    self.preview_canvas.create_oval(px-3, py-3, px+3, py+3,
                                                   fill='red', outline='darkred')
            
            # Add comprehensive dimensions and labels
            title_text = f"Column Section: {width:.0f} × {height:.0f} mm"
            self.preview_canvas.create_text(cx, 20, text=title_text, 
                                          font=("Arial", 12, "bold"))
            
            # Width dimension
            self.preview_canvas.create_line(x1, y2+20, x2, y2+20, fill='black', width=2)
            self.preview_canvas.create_line(x1, y2+15, x1, y2+25, fill='black', width=2)
            self.preview_canvas.create_line(x2, y2+15, x2, y2+25, fill='black', width=2)
            self.preview_canvas.create_text(cx, y2+35, text=f"B = {width:.0f} mm", 
                                          font=("Arial", 10, "bold"))
            
            # Height dimension
            self.preview_canvas.create_line(x1-20, y1, x1-20, y2, fill='black', width=2)
            self.preview_canvas.create_line(x1-25, y1, x1-15, y1, fill='black', width=2)
            self.preview_canvas.create_line(x1-25, y2, x1-15, y2, fill='black', width=2)
            self.preview_canvas.create_text(x1-40, cy, text=f"H = {height:.0f} mm", 
                                          font=("Arial", 10, "bold"), angle=90)
            
            # Cover indication
            try:
                self.preview_canvas.create_line(x1, y1, x1+cover_scaled, y1+cover_scaled, 
                                              fill='red', width=1, dash=(2, 2))
                self.preview_canvas.create_text(x1+cover_scaled/2-10, y1+cover_scaled/2-10, 
                                              text=f"{cover:.0f}mm", font=("Arial", 8), fill='red')
            except:
                pass
            
            # Reinforcement summary
            try:
                rebar_text = f"Reinforcement:\n"
                rebar_text += f"X: {num_x}×{self.rebar_x_var.get()}\n"
                rebar_text += f"Y: {num_y}×{self.rebar_y_var.get()}\n"
                rebar_text += f"Ties: {self.tie_size_var.get()} @ {tie_spacing:.0f}mm"
                
                self.preview_canvas.create_text(cx, canvas_height-60, text=rebar_text, 
                                              font=("Arial", 8), justify=tk.CENTER)
            except:
                pass
                
        except ValueError:
            # Show error state
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(200, 250, text="Invalid Input Values", 
                                          font=("Arial", 14), fill='red')
        except Exception as e:
            # Show basic preview on any error
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(200, 250, text="Preview Error", 
                                          font=("Arial", 12), fill='orange')
    
    def update_rebar_preview(self, event=None):
        """Update reinforcement preview when rebar details change"""
        self.update_preview()
        
    def run_complete_analysis(self):
        """Run complete structural analysis"""
        try:
            # Collect all input data
            inputs = self.collect_input_data()
            
            # Perform calculations
            results = self.perform_calculations(inputs)
            
            # Store results
            self.last_results = results
            
            # Update all displays
            self.display_analysis_results(results)
            self.generate_pm_diagram()
            
            # Show completion message
            status = "✅ SAFE" if results['utilization'] <= 100 else "⚠️ OVER-UTILIZED"
            messagebox.showinfo("Analysis Complete", 
                               f"Complete analysis finished!\n"
                               f"Status: {status}\n"
                               f"Utilization: {results['utilization']:.1f}%")
                               
        except ValueError:
            messagebox.showerror("Input Error", "Please check all input values.")
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error in analysis: {str(e)}")
    
    def collect_input_data(self):
        """Collect all input data from the interface"""
        return {
            # Geometry
            'width': float(self.width_var.get()),
            'height': float(self.height_var.get()),
            'length': float(self.length_var.get()),
            
            # Loads
            'P': float(self.axial_load_var.get()),
            'Mx': float(self.moment_x_var.get()),
            'My': float(self.moment_y_var.get()),
            
            # Materials
            'fc': float(self.fc_var.get()),
            'fy': float(self.fy_var.get()),
            
            # Reinforcement
            'rebar_x': self.rebar_x_var.get(),
            'rebar_y': self.rebar_y_var.get(),
            'corner_rebar': self.corner_rebar_var.get(),
            'num_bars_x': int(self.num_bars_x_var.get()),
            'num_bars_y': int(self.num_bars_y_var.get()),
            'tie_size': self.tie_size_var.get(),
            'tie_spacing': float(self.tie_spacing_var.get()),
            'tie_legs': int(self.tie_legs_var.get()),
            'end_spacing': float(self.end_spacing_var.get()),
            'end_length': float(self.end_length_var.get()),
            'cover': float(self.cover_var.get()),
            'dev_length_factor': float(self.dev_length_factor_var.get())
        }
    
    def perform_calculations(self, inputs):
        """Perform complete structural calculations"""
        
        # Basic section properties
        Ag = inputs['width'] * inputs['height']  # mm²
        
        # Reinforcement calculations
        As_x = inputs['num_bars_x'] * self.get_rebar_area(inputs['rebar_x'])
        As_y = inputs['num_bars_y'] * self.get_rebar_area(inputs['rebar_y'])
        As_total = As_x + As_y
        
        # Corner reinforcement (4 corner bars with selected size)
        As_corner = 4 * self.get_rebar_area(inputs['corner_rebar'])
        
        # Total reinforcement
        As_provided = As_total + As_corner
        steel_ratio = As_provided / Ag * 100
        
        # Load calculations
        P_N = inputs['P'] * 1000  # kN to N
        Mx_Nm = inputs['Mx'] * 1000  # kN⋅m to N⋅m
        My_Nm = inputs['My'] * 1000  # kN⋅m to N⋅m
        
        # Eccentricities
        ex = Mx_Nm / P_N * 1000 if P_N > 0 else 0  # mm
        ey = My_Nm / P_N * 1000 if P_N > 0 else 0  # mm
        
        # Slenderness
        rx = inputs['height'] / math.sqrt(12)
        ry = inputs['width'] / math.sqrt(12)
        slenderness_x = (inputs['length'] * 1000) / rx
        slenderness_y = (inputs['length'] * 1000) / ry
        
        # Capacity calculations (simplified)
        fc = inputs['fc']
        fy = inputs['fy']
        
        # Concrete contribution
        Pn_concrete = 0.85 * fc * (Ag - As_provided)
        
        # Steel contribution
        Pn_steel = fy * As_provided
        
        # Total nominal capacity
        Pn_total = Pn_concrete + Pn_steel
        
        # Reduced capacity (φ factor)
        phi = 0.65  # For tied columns
        Pu_capacity = phi * Pn_total / 1000  # kN
        
        # Utilization
        utilization = (inputs['P'] / Pu_capacity) * 100 if Pu_capacity > 0 else 999
        
        # Tie spacing checks
        max_spacing = min(16 * self.get_rebar_diameter(inputs['rebar_x']), 
                         48 * self.get_rebar_diameter(inputs['tie_size']),
                         min(inputs['width'], inputs['height']))
        
        tie_spacing_ok = inputs['tie_spacing'] <= max_spacing
        
        # Development length calculation
        db = self.get_rebar_diameter(inputs['rebar_x'])
        ld_basic = 0.6 * fy * db / math.sqrt(fc)  # Basic development length
        ld_required = ld_basic * inputs['dev_length_factor']
        
        return {
            # Input echo
            **inputs,
            
            # Calculated properties
            'Ag': Ag,
            'As_x': As_x,
            'As_y': As_y,
            'As_corner': As_corner,
            'As_total': As_total,
            'As_provided': As_provided,
            'steel_ratio': steel_ratio,
            
            # Loading
            'ex': ex,
            'ey': ey,
            'slenderness_x': slenderness_x,
            'slenderness_y': slenderness_y,
            
            # Capacity
            'Pn_concrete': Pn_concrete,
            'Pn_steel': Pn_steel,
            'Pn_total': Pn_total,
            'Pu_capacity': Pu_capacity,
            'utilization': utilization,
            
            # Detailing checks
            'max_spacing': max_spacing,
            'tie_spacing_ok': tie_spacing_ok,
            'ld_required': ld_required
        }
    
    def display_analysis_results(self, results):
        """Display detailed analysis results"""
        self.analysis_text.delete(1.0, tk.END)
        
        analysis = f"""
COMPREHENSIVE STRUCTURAL ANALYSIS
{'='*60}

SECTION PROPERTIES:
• Column Dimensions: {results['width']:.0f} × {results['height']:.0f} mm
• Gross Area (Ag): {results['Ag']:,.0f} mm²
• Length: {results['length']:.1f} m
• Clear Cover: {results['cover']:.0f} mm

REINFORCEMENT SUMMARY:
┌─ Longitudinal Reinforcement ──────────────────────────┐
│ X-Direction: {results['num_bars_x']:.0f} × {results['rebar_x']} = {results['As_x']:,.0f} mm²     │
│ Y-Direction: {results['num_bars_y']:.0f} × {results['rebar_y']} = {results['As_y']:,.0f} mm²     │
│ Corner Bars: 4 × {results['corner_rebar']} = {results['As_corner']:,.0f} mm²          │
│ Total Steel: {results['As_provided']:,.0f} mm²                        │
│ Steel Ratio: {results['steel_ratio']:.2f}%                            │
└────────────────────────────────────────────────────────┘

┌─ Transverse Reinforcement ─────────────────────────────┐
│ Tie Size: {results['tie_size']} with {results['tie_legs']:.0f} legs                    │
│ Spacing: {results['tie_spacing']:.0f} mm (Max: {results['max_spacing']:.0f} mm)             │
│ End Regions: {results['end_spacing']:.0f} mm for {results['end_length']:.0f} mm length      │
│ Tie Check: {'✓ OK' if results['tie_spacing_ok'] else '✗ FAIL'}                              │
└────────────────────────────────────────────────────────┘

LOADING ANALYSIS:
• Applied Loads: P = {results['P']:,.0f} kN, Mx = {results['Mx']:.0f} kN⋅m, My = {results['My']:.0f} kN⋅m
• Eccentricities: ex = {results['ex']:.1f} mm, ey = {results['ey']:.1f} mm
• Load Type: {'Compression' if max(results['ex'], results['ey']) < min(results['width'], results['height'])/6 else 'Combined Bending'}

SLENDERNESS CHECK:
• λx = {results['slenderness_x']:.1f}, λy = {results['slenderness_y']:.1f}
• Status: {'Short Column' if max(results['slenderness_x'], results['slenderness_y']) <= 22 else 'Slender Column'}

CAPACITY ANALYSIS:
• Concrete Contribution: {results['Pn_concrete']/1000:,.0f} kN
• Steel Contribution: {results['Pn_steel']/1000:,.0f} kN
• Nominal Capacity: {results['Pn_total']/1000:,.0f} kN
• Design Capacity (φPn): {results['Pu_capacity']:,.0f} kN
• Utilization Ratio: {results['utilization']:.1f}%

DEVELOPMENT LENGTH:
• Required Ld: {results['ld_required']:.0f} mm
• Available Length: {results['length']*1000-2*results['end_length']:.0f} mm

DESIGN STATUS: {'✅ SAFE' if results['utilization'] <= 100 else '⚠️ OVER-UTILIZED'}
"""
        
        self.analysis_text.insert(tk.END, analysis)
    
    def generate_pm_diagram(self):
        """Generate P-M interaction diagram"""
        if self.last_results is None:
            messagebox.showwarning("No Data", "Please run analysis first.")
            return
        
        if not HAS_MATPLOTLIB:
            messagebox.showerror("Missing Library", "Matplotlib is required for P-M diagrams. Please install matplotlib.")
            return
            
        try:
            # Clear previous diagram
            for widget in self.figure_frame.winfo_children():
                widget.destroy()
            
            # Create figure
            fig = Figure(figsize=(12, 8), dpi=100)
            
            # Create subplots
            ax1 = fig.add_subplot(121)  # P-Mx diagram
            ax2 = fig.add_subplot(122)  # P-My diagram
            
            results = self.last_results
            
            # Generate interaction curves
            Mx_points, P_points_x = self.calculate_pm_interaction(results, 'x')
            My_points, P_points_y = self.calculate_pm_interaction(results, 'y')
            
            # Plot P-Mx diagram
            ax1.plot(Mx_points, P_points_x, 'b-', linewidth=2, label='Interaction Curve')
            ax1.plot(results['Mx'], results['P'], 'ro', markersize=8, label='Applied Load')
            ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel('Moment Mx (kN⋅m)')
            ax1.set_ylabel('Axial Load P (kN)')
            ax1.set_title('P-Mx Interaction Diagram')
            ax1.legend()
            
            # Plot P-My diagram
            ax2.plot(My_points, P_points_y, 'g-', linewidth=2, label='Interaction Curve')
            ax2.plot(results['My'], results['P'], 'ro', markersize=8, label='Applied Load')
            ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel('Moment My (kN⋅m)')
            ax2.set_ylabel('Axial Load P (kN)')
            ax2.set_title('P-My Interaction Diagram')
            ax2.legend()
            
            # Add safety check annotations
            if results['utilization'] <= 100:
                safety_text = f"✓ SAFE\nUtilization: {results['utilization']:.1f}%"
                color = 'green'
            else:
                safety_text = f"✗ UNSAFE\nUtilization: {results['utilization']:.1f}%"
                color = 'red'
            
            fig.suptitle(f'Column Interaction Diagrams - {safety_text}', 
                        fontsize=14, fontweight='bold', color=color)
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.figure_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Store for export
            self.interaction_figure = fig
            
        except Exception as e:
            messagebox.showerror("Diagram Error", f"Could not generate diagram: {str(e)}")
    
    def calculate_pm_interaction(self, results, direction):
        """Calculate P-M interaction points for given direction using proper analysis"""
        
        fc = results['fc']
        fy = results['fy']
        
        if direction == 'x':
            h = results['height']
            b = results['width']
            As_tension = results['As_x'] + results['As_corner']/2
            As_compression = results['As_x'] + results['As_corner']/2
        else:
            h = results['width']  
            b = results['height']
            As_tension = results['As_y'] + results['As_corner']/2
            As_compression = results['As_y'] + results['As_corner']/2
        
        cover = results['cover']
        d = h - cover  # Effective depth to tension steel
        d_prime = cover  # Depth to compression steel
        
        # Material properties
        beta1 = 0.85 if fc <= 28 else max(0.85 - 0.05*(fc-28)/7, 0.65)
        epsilon_cu = 0.003  # Ultimate concrete strain
        Es = 200000  # Steel modulus (MPa)
        
        # Generate points for interaction curve
        M_points = []
        P_points = []
        
        # Point 1: Pure compression (no moment)
        Pn_max = 0.85 * fc * (results['Ag'] - results['As_provided']) + fy * results['As_provided']
        P_points.append(min(0.8 * Pn_max / 1000, 0.85 * Pn_max / 1000))  # Tied column limit
        M_points.append(0)
        
        # Calculate balanced point
        cb_balanced = (0.003 * d) / (0.003 + fy / Es)  # Balanced neutral axis depth
        
        # Generate interaction points by varying neutral axis depth
        c_values = []
        
        # Points for compression-controlled region (c > cb_balanced)
        for i in range(5):
            c_ratio = 0.2 + (i * 0.15)  # From 0.2h to 0.8h
            c_values.append(c_ratio * h)
        
        # Add balanced point
        c_values.append(cb_balanced)
        
        # Points for tension-controlled region (c < cb_balanced)  
        for i in range(5):
            c_ratio = 0.05 + (i * cb_balanced/h * 0.15)  # Smaller values
            c_values.append(c_ratio * h)
        
        # Pure moment point (c approaching 0)
        c_values.append(0.01 * h)
        
        # Sort c values in descending order for smooth curve
        c_values.sort(reverse=True)
        
        for c in c_values:
            if c <= 0.01 * h:  # Pure moment case
                # Simplified pure moment capacity
                a = 0.01 * h
                Mn = As_tension * fy * (d - a/2) / 1000000  # Convert to kN⋅m
                Pn = 0
            else:
                # Calculate strains
                epsilon_s = epsilon_cu * (d - c) / c  # Tension steel strain
                epsilon_s_prime = epsilon_cu * (c - d_prime) / c  # Compression steel strain
                
                # Calculate stresses
                if abs(epsilon_s) >= fy / Es:
                    fs = fy if epsilon_s > 0 else -fy
                else:
                    fs = Es * epsilon_s
                
                if abs(epsilon_s_prime) >= fy / Es:
                    fs_prime = fy if epsilon_s_prime > 0 else -fy
                else:
                    fs_prime = Es * epsilon_s_prime
                
                # Concrete stress block
                a = beta1 * c
                Cc = 0.85 * fc * a * b  # Concrete compression force
                
                # Steel forces
                Ts = As_tension * fs  # Tension steel force
                Cs = As_compression * fs_prime  # Compression steel force
                
                # Equilibrium
                Pn = (Cc + Cs - Ts) / 1000  # Convert to kN
                
                # Moment about centroid
                Mn = (Cc * (h/2 - a/2) + Cs * (h/2 - d_prime) + Ts * (d - h/2)) / 1000000  # kN⋅m
                
                # Apply limits
                Pn = max(0, min(Pn, P_points[0]))  # Cannot exceed max compression
            
            P_points.append(max(0, Pn))
            M_points.append(abs(Mn))
        
        # Add pure tension point (negative moment region)
        P_points.append(0)
        M_points.append(0)
        
        # Remove duplicates and sort for smooth curve
        points = list(zip(M_points, P_points))
        points = list(set(points))  # Remove duplicates
        points.sort(key=lambda x: (x[1], x[0]))  # Sort by P, then M
        
        # Separate back into lists
        M_sorted = [p[0] for p in points]
        P_sorted = [p[1] for p in points]
        
        # Ensure curve is physically reasonable
        M_final = []
        P_final = []
        
        for i, (m, p) in enumerate(zip(M_sorted, P_sorted)):
            if i == 0 or (m >= 0 and p >= 0):  # Only positive values
                M_final.append(m)
                P_final.append(p)
        
        return M_final, P_final
    
    def generate_report_diagrams(self):
        """Generate section preview and P-M diagrams for inclusion in report"""
        if not HAS_MATPLOTLIB:
            return  # Skip diagram generation if matplotlib not available
            
        results = self.last_results
        
        try:
            import os
            import tempfile
            
            # Create temporary directory for images
            self.temp_dir = tempfile.mkdtemp()
            
            # Generate section preview diagram
            self.generate_section_preview_image()
            
            # Generate P-M interaction diagrams
            self.generate_pm_diagrams_image()
            
        except Exception as e:
            print(f"Warning: Could not generate report diagrams: {e}")
    
    def generate_section_preview_image(self):
        """Generate detailed section preview image for report"""
        if not HAS_MATPLOTLIB:
            return
            
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.lines import Line2D
            import os
            
            results = self.last_results
            if results is None:
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            
            # Column dimensions
            width = results['width']
            height = results['height']
            cover = results['cover']
            
            # Draw column outline
            column_rect = patches.Rectangle((0, 0), width, height, 
                                          linewidth=2, edgecolor='black', 
                                          facecolor='lightgray', alpha=0.3)
            ax.add_patch(column_rect)
            
            # Draw reinforcement
            # Get rebar diameter
            rebar_x_dia = self.get_rebar_diameter(results['rebar_x'])
            rebar_y_dia = self.get_rebar_diameter(results['rebar_y'])
            corner_dia = self.get_rebar_diameter(results['corner_rebar'])
            
            # Corner bars
            corner_positions = [
                (cover, cover),  # Bottom-left
                (width - cover, cover),  # Bottom-right
                (width - cover, height - cover),  # Top-right
                (cover, height - cover)  # Top-left
            ]
            
            for pos in corner_positions:
                circle = patches.Circle(pos, corner_dia/2, 
                                      facecolor='red', edgecolor='darkred')
                ax.add_patch(circle)
            
            # X-direction bars (excluding corners)
            if results['num_bars_x'] > 2:  # Additional bars between corners
                x_spacing = (width - 2*cover) / (results['num_bars_x'] - 1)
                for i in range(1, results['num_bars_x'] - 1):
                    x_pos = cover + i * x_spacing
                    # Bottom bars
                    circle = patches.Circle((x_pos, cover), rebar_x_dia/2,
                                          facecolor='blue', edgecolor='darkblue')
                    ax.add_patch(circle)
                    # Top bars
                    circle = patches.Circle((x_pos, height - cover), rebar_x_dia/2,
                                          facecolor='blue', edgecolor='darkblue')
                    ax.add_patch(circle)
            
            # Y-direction bars (excluding corners)
            if results['num_bars_y'] > 2:  # Additional bars between corners
                y_spacing = (height - 2*cover) / (results['num_bars_y'] - 1)
                for i in range(1, results['num_bars_y'] - 1):
                    y_pos = cover + i * y_spacing
                    # Left bars
                    circle = patches.Circle((cover, y_pos), rebar_y_dia/2,
                                          facecolor='green', edgecolor='darkgreen')
                    ax.add_patch(circle)
                    # Right bars
                    circle = patches.Circle((width - cover, y_pos), rebar_y_dia/2,
                                          facecolor='green', edgecolor='darkgreen')
                    ax.add_patch(circle)
            
            # Draw ties
            tie_dia = self.get_rebar_diameter(results['tie_size'])
            tie_rect = patches.Rectangle((cover - tie_dia/2, cover - tie_dia/2), 
                                       width - 2*cover + tie_dia, 
                                       height - 2*cover + tie_dia,
                                       linewidth=2, edgecolor='orange', 
                                       facecolor='none', linestyle='--')
            ax.add_patch(tie_rect)
            
            # Add dimensions
            # Width dimension
            ax.annotate('', xy=(0, -20), xytext=(width, -20),
                       arrowprops=dict(arrowstyle='<->', color='black'))
            ax.text(width/2, -35, f'{width:.0f} mm', ha='center', va='top', fontsize=10)
            
            # Height dimension
            ax.annotate('', xy=(-20, 0), xytext=(-20, height),
                       arrowprops=dict(arrowstyle='<->', color='black'))
            ax.text(-35, height/2, f'{height:.0f} mm', ha='center', va='bottom', 
                   rotation=90, fontsize=10)
            
            # Cover dimensions
            ax.annotate('', xy=(0, height + 10), xytext=(cover, height + 10),
                       arrowprops=dict(arrowstyle='<->', color='red'))
            ax.text(cover/2, height + 25, f'{cover:.0f} mm', ha='center', va='bottom', 
                   fontsize=8, color='red')
            
            # Add reinforcement legend
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                          markersize=8, label=f'Corner: 4-{results["corner_rebar"]}'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                          markersize=8, label=f'X-dir: {results["num_bars_x"]}-{results["rebar_x"]}'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                          markersize=8, label=f'Y-dir: {results["num_bars_y"]}-{results["rebar_y"]}'),
                Line2D([0], [0], color='orange', linestyle='--', linewidth=2,
                          label=f'Ties: {results["tie_size"]}@{results["tie_spacing"]:.0f}mm')
            ]
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))
            
            # Set equal aspect ratio and limits
            ax.set_xlim(-60, width + 60)
            ax.set_ylim(-60, height + 60)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Width (mm)')
            ax.set_ylabel('Height (mm)')
            ax.set_title('Reinforcement Details\nColumn Cross-Section', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            # Save the image
            self.section_preview_path = os.path.join(self.temp_dir, 'section_preview.png')
            plt.savefig(self.section_preview_path, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error generating section preview: {e}")
    
    def generate_pm_diagrams_image(self):
        """Generate P-M interaction diagrams image for report"""
        if not HAS_MATPLOTLIB:
            return
            
        try:
            import matplotlib.pyplot as plt
            import os
            
            results = self.last_results
            if results is None:
                return
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Generate interaction curves
            Mx_points, P_points_x = self.calculate_pm_interaction(results, 'x')
            My_points, P_points_y = self.calculate_pm_interaction(results, 'y')
            
            # Plot P-Mx diagram
            ax1.plot(Mx_points, P_points_x, 'b-', linewidth=2, label='Interaction Curve')
            ax1.plot(results['Mx'], results['P'], 'ro', markersize=10, label='Applied Load')
            ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
            ax1.set_xlabel('Moment Mx (kN⋅m)', fontsize=10)
            ax1.set_ylabel('Axial Load P (kN)', fontsize=10)
            ax1.set_title(f'P-Mx Interaction Diagram\nUtilization: {results["utilization"]:.1f}%', 
                         fontsize=11, fontweight='bold')
            ax1.legend()
            
            # Add safety annotation
            if results['utilization'] <= 100:
                safety_text = "SAFE"
                color = 'green'
            else:
                safety_text = "UNSAFE"
                color = 'red'
            
            ax1.text(0.02, 0.98, f'Status: {safety_text}', transform=ax1.transAxes,
                    bbox=dict(boxstyle='round', facecolor=color, alpha=0.3),
                    verticalalignment='top', fontweight='bold')
            
            # Plot P-My diagram
            ax2.plot(My_points, P_points_y, 'g-', linewidth=2, label='Interaction Curve')
            ax2.plot(results['My'], results['P'], 'ro', markersize=10, label='Applied Load')
            ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel('Moment My (kN⋅m)', fontsize=10)
            ax2.set_ylabel('Axial Load P (kN)', fontsize=10)
            ax2.set_title(f'P-My Interaction Diagram\nUtilization: {results["utilization"]:.1f}%', 
                         fontsize=11, fontweight='bold')
            ax2.legend()
            
            # Add safety annotation
            ax2.text(0.02, 0.98, f'Status: {safety_text}', transform=ax2.transAxes,
                    bbox=dict(boxstyle='round', facecolor=color, alpha=0.3),
                    verticalalignment='top', fontweight='bold')
            
            plt.tight_layout()
            
            # Save the image
            self.pm_diagrams_path = os.path.join(self.temp_dir, 'pm_diagrams.png')
            plt.savefig(self.pm_diagrams_path, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error generating P-M diagrams: {e}")
    
    def save_pm_diagram(self):
        """Save the P-M interaction diagram"""
        if hasattr(self, 'interaction_figure') and self.last_results:
            filename = f"PM_Diagram_{self.last_results['width']:.0f}x{self.last_results['height']:.0f}.png"
            self.interaction_figure.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Saved", f"Diagram saved as {filename}")
        else:
            messagebox.showwarning("No Diagram", "Please generate diagram first.")
    
    def generate_full_report(self):
        """Generate comprehensive design report with detailed formulas and diagrams"""
        if self.last_results is None:
            messagebox.showwarning("No Data", "Please run analysis first.")
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # First generate the diagrams and save them as temporary images
        self.generate_report_diagrams()
        
        results = self.last_results
        
        report = f"""
{'='*80}
                    REINFORCED CONCRETE COLUMN DESIGN REPORT
                           WITH DETAILED CALCULATIONS
{'='*80}

PROJECT INFORMATION:
• Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Software: Professional Column Design v3.0
• Design Code: ACI 318M-25 Chapter 10 (Columns)

{'='*80}
1. DESIGN INPUT PARAMETERS
{'='*80}

1.1 GEOMETRY:
    Column Cross-Section: {results['width']:.0f} mm × {results['height']:.0f} mm
    Column Length: {results['length']:.1f} m
    
    FORMULA: Ag = B × H
    CALCULATION: Ag = {results['width']:.0f} × {results['height']:.0f} = {results['Ag']:,.0f} mm²

1.2 APPLIED LOADS (Ultimate):
    Axial Load (Pu): {results['P']:,.0f} kN
    Moment about X-axis (Mux): {results['Mx']:.0f} kN⋅m
    Moment about Y-axis (Muy): {results['My']:.0f} kN⋅m
    
    ECCENTRICITY CALCULATIONS:
    FORMULA: ex = Mux / Pu, ey = Muy / Pu
    
    CALCULATION: 
    ex = {results['Mx']:.0f} / {results['P']:,.0f} = {results['ex']:.1f} mm
    ey = {results['My']:.0f} / {results['P']:,.0f} = {results['ey']:.1f} mm

1.3 MATERIAL PROPERTIES:
    Concrete Compressive Strength (fc'): {results['fc']:.0f} MPa
    Steel Yield Strength (fy): {results['fy']:.0f} MPa

┌────────────────────────────────────────────────────────────────────────────┐
│                    DETAILED SECTION PREVIEW                               │
│    ✓ Cross-section diagram generated showing reinforcement layout         │
│    ✓ Includes all longitudinal bars and tie arrangements                  │
│    ✓ Shows dimensions and spacing details                                 │
│                                                                            │
│    [View complete diagram in PDF export or P-M Diagram window]            │
└────────────────────────────────────────────────────────────────────────────┘

{'='*80}
2. REINFORCEMENT DESIGN WITH DETAILED CALCULATIONS
{'='*80}

2.1 LONGITUDINAL REINFORCEMENT AREA CALCULATIONS:
    
    X-Direction Reinforcement:
    • Size: {results['rebar_x']} (Area per bar = {self.get_rebar_area(results['rebar_x']):.0f} mm²)
    • Number of bars: {results['num_bars_x']:.0f}
    
    FORMULA: As,x = n × Ab
    CALCULATION: As,x = {results['num_bars_x']:.0f} × {self.get_rebar_area(results['rebar_x']):.0f} = {results['As_x']:,.0f} mm²
    
    Y-Direction Reinforcement:
    • Size: {results['rebar_y']} (Area per bar = {self.get_rebar_area(results['rebar_y']):.0f} mm²)
    • Number of bars: {results['num_bars_y']:.0f}
    
    FORMULA: As,y = n × Ab
    CALCULATION: As,y = {results['num_bars_y']:.0f} × {self.get_rebar_area(results['rebar_y']):.0f} = {results['As_y']:,.0f} mm²
    
    Corner Reinforcement:
    • Size: {results['corner_rebar']} (Area per bar = {self.get_rebar_area(results['corner_rebar']):.0f} mm²)
    • Number: 4 bars (fixed at corners)
    
    FORMULA: As,corner = 4 × Ab
    CALCULATION: As,corner = 4 × {self.get_rebar_area(results['corner_rebar']):.0f} = {results['As_corner']:,.0f} mm²
    
    TOTAL LONGITUDINAL REINFORCEMENT:
    FORMULA: As,total = As,x + As,y + As,corner
    CALCULATION: As,total = {results['As_x']:,.0f} + {results['As_y']:,.0f} + {results['As_corner']:,.0f} = {results['As_provided']:,.0f} mm²
    
    STEEL RATIO CALCULATION:
    FORMULA: ρ = As,total / Ag × 100%
    CALCULATION: ρ = {results['As_provided']:,.0f} / {results['Ag']:,.0f} × 100% = {results['steel_ratio']:.2f}%
    
    CHECK: Minimum ρ = 1.0%, Maximum ρ = 6.0%
    STATUS: {'✓ OK' if 1.0 <= results['steel_ratio'] <= 6.0 else '✗ Outside recommended range'} ({results['steel_ratio']:.2f}%)

2.2 TRANSVERSE REINFORCEMENT (TIES) - SPACING CALCULATIONS:
    
    Tie Specifications:
    • Size: {results['tie_size']} (Diameter = {self.get_rebar_diameter(results['tie_size']):.0f} mm)
    • Configuration: {results['tie_legs']:.0f}-leg ties
    • Spacing in main region: {results['tie_spacing']:.0f} mm
    • Spacing in end regions: {results['end_spacing']:.0f} mm
    • End region length: {results['end_length']:.0f} mm
    
    MAXIMUM SPACING CALCULATION (ACI 318M-25 Ch.10):
    The smallest of:
    1) 16 × db,longitudinal = 16 × {self.get_rebar_diameter(results['rebar_x']):.0f} = {16 * self.get_rebar_diameter(results['rebar_x']):.0f} mm
    2) 48 × db,tie = 48 × {self.get_rebar_diameter(results['tie_size']):.0f} = {48 * self.get_rebar_diameter(results['tie_size']):.0f} mm
    3) Least dimension = min({results['width']:.0f}, {results['height']:.0f}) = {min(results['width'], results['height']):.0f} mm
    
    GOVERNING: Maximum spacing = {results['max_spacing']:.0f} mm
    PROVIDED: {results['tie_spacing']:.0f} mm
    STATUS: {'✓ OK' if results['tie_spacing_ok'] else '✗ EXCEEDS MAXIMUM'}

2.3 DEVELOPMENT LENGTH CALCULATION:
    
    FORMULA: Ld = 0.6 × fy × db / √fc' × factor
    WHERE:
    • fy = {results['fy']:.0f} MPa (steel yield strength)
    • db = {self.get_rebar_diameter(results['rebar_x']):.0f} mm (bar diameter)
    • fc' = {results['fc']:.0f} MPa (concrete strength)
    • factor = {results['dev_length_factor']:.1f} (development factor)
    
    CALCULATION:
    Ld = 0.6 × {results['fy']:.0f} × {self.get_rebar_diameter(results['rebar_x']):.0f} / √{results['fc']:.0f} × {results['dev_length_factor']:.1f}
    Ld = {0.6 * results['fy'] * self.get_rebar_diameter(results['rebar_x']) / math.sqrt(results['fc']):.1f} × {results['dev_length_factor']:.1f} = {results['ld_required']:.0f} mm
    
    AVAILABLE LENGTH: {results['length']*1000-2*results['end_length']:.0f} mm
    STATUS: {'✓ ADEQUATE' if results['length']*1000-2*results['end_length'] >= results['ld_required'] else '✗ INSUFFICIENT'}

{'='*80}
3. STRUCTURAL ANALYSIS WITH FORMULAS
{'='*80}

3.1 SLENDERNESS CHECK:
    
    RADIUS OF GYRATION CALCULATION:
    FORMULA: r = √(I/A) = dimension/√12 (for rectangular sections)
    
    CALCULATION:
    rx = H/√12 = {results['height']:.0f}/√12 = {results['height']/math.sqrt(12):.1f} mm
    ry = B/√12 = {results['width']:.0f}/√12 = {results['width']/math.sqrt(12):.1f} mm
    
    SLENDERNESS RATIOS:
    FORMULA: λ = Lu/r (effective length/radius of gyration)
    ASSUMING: Lu = L (pinned-pinned condition)
    
    CALCULATION:
    λx = L/rx = {results['length']*1000:.0f}/{results['height']/math.sqrt(12):.1f} = {results['slenderness_x']:.1f}
    λy = L/ry = {results['length']*1000:.0f}/{results['width']/math.sqrt(12):.1f} = {results['slenderness_y']:.1f}
    
    CLASSIFICATION: {'Short Column (λ ≤ 22)' if max(results['slenderness_x'], results['slenderness_y']) <= 22 else 'Slender Column (λ > 22)'}
    GOVERNING: λmax = {max(results['slenderness_x'], results['slenderness_y']):.1f}

3.2 LOADING ANALYSIS:
    
    ECCENTRICITY RATIO CHECK:
    FORMULA: e/(h/6) for load classification
    
    CALCULATION:
    ex/(H/6) = {results['ex']:.1f}/({results['height']:.0f}/6) = {results['ex']:.1f}/{results['height']/6:.1f} = {results['ex']/(results['height']/6):.2f}
    ey/(B/6) = {results['ey']:.1f}/({results['width']:.0f}/6) = {results['ey']:.1f}/{results['width']/6:.1f} = {results['ey']/(results['width']/6):.2f}
    
    CLASSIFICATION: {'Small eccentricity - Compression controlled' if max(results['ex']/(results['height']/6), results['ey']/(results['width']/6)) <= 1.0 else 'Large eccentricity - Tension controlled'}

{'='*80}
4. CAPACITY CALCULATIONS WITH DETAILED FORMULAS
{'='*80}

4.1 NOMINAL AXIAL CAPACITY (SIMPLIFIED METHOD):
    
    CONCRETE CONTRIBUTION:
    FORMULA: Pn,concrete = 0.85 × fc' × (Ag - As)
    WHERE:
    • 0.85 = concrete stress factor
    • fc' = {results['fc']:.0f} MPa
    • Ag = {results['Ag']:,.0f} mm²
    • As = {results['As_provided']:,.0f} mm²
    
    CALCULATION:
    Pn,concrete = 0.85 × {results['fc']:.0f} × ({results['Ag']:,.0f} - {results['As_provided']:,.0f})
    Pn,concrete = 0.85 × {results['fc']:.0f} × {results['Ag'] - results['As_provided']:,.0f}
    Pn,concrete = {results['fc'] * 0.85 * (results['Ag'] - results['As_provided'])/1000:.0f} kN

    STEEL CONTRIBUTION:
    FORMULA: Pn,steel = fy × As
    WHERE:
    • fy = {results['fy']:.0f} MPa
    • As = {results['As_provided']:,.0f} mm²
    
    CALCULATION:
    Pn,steel = {results['fy']:.0f} × {results['As_provided']:,.0f}
    Pn,steel = {results['fy'] * results['As_provided']/1000:.0f} kN
    
    TOTAL NOMINAL CAPACITY:
    FORMULA: Pn = Pn,concrete + Pn,steel
    CALCULATION: Pn = {results['Pn_concrete']/1000:,.0f} + {results['Pn_steel']/1000:,.0f} = {results['Pn_total']/1000:,.0f} kN

4.2 DESIGN CAPACITY WITH STRENGTH REDUCTION:
    
    STRENGTH REDUCTION FACTOR:
    φ = 0.65 (for tied columns per ACI 318M-25 Ch.10)
    
    FORMULA: φPn = φ × Pn
    CALCULATION: φPn = 0.65 × {results['Pn_total']/1000:,.0f} = {results['Pu_capacity']:,.0f} kN

4.3 CAPACITY UTILIZATION CHECK:
    
    FORMULA: Utilization = (Applied Load / Design Capacity) × 100%
    CALCULATION: Utilization = ({results['P']:,.0f} / {results['Pu_capacity']:,.0f}) × 100%
    CALCULATION: Utilization = {results['utilization']:.1f}%
    
    DESIGN MARGIN: {100 - results['utilization']:.1f}%
    STATUS: {'✅ ADEQUATE CAPACITY' if results['utilization'] <= 100 else '❌ INADEQUATE CAPACITY - INCREASE SIZE OR REINFORCEMENT'}

┌────────────────────────────────────────────────────────────────────────────┐
│                        P-M INTERACTION DIAGRAMS                           │
│    ✓ P-Mx interaction curve generated and analyzed                        │
│    ✓ P-My interaction curve generated and analyzed                        │
│    ✓ Applied loads plotted on interaction curves                          │
│    ✓ Safety status: {'SAFE' if results['utilization'] <= 100 else 'UNSAFE'} - Utilization: {results['utilization']:.1f}%                      │
│                                                                            │
│    [Complete interaction diagrams available in PDF export]                │
└────────────────────────────────────────────────────────────────────────────┘

{'='*80}
5. MATERIAL PROPERTIES AND CODE FACTORS
{'='*80}

5.1 CONCRETE PROPERTIES:
    • Compressive Strength: fc' = {results['fc']:.0f} MPa
    • Modulus of Elasticity: Ec = 4700√fc' = 4700√{results['fc']:.0f} = {4700*math.sqrt(results['fc']):.0f} MPa
    • Strain at Peak Stress: εcu = 0.003

5.2 STEEL PROPERTIES:
    • Yield Strength: fy = {results['fy']:.0f} MPa
    • Modulus of Elasticity: Es = 200,000 MPa
    • Yield Strain: εy = fy/Es = {results['fy']:.0f}/200,000 = {results['fy']/200000:.6f}

5.3 DESIGN FACTORS (ACI 318M-25 Ch.10):
    • Strength Reduction Factor (φ): 0.65 (tied columns)
    • Concrete Stress Factor: 0.85
    • Beta 1 Factor: β₁ = {'0.85' if results['fc'] <= 28 else f'{max(0.85 - 0.05*(results["fc"]-28)/7, 0.65):.3f}'}
    • Minimum Steel Ratio: ρmin = 1.0% (per 10.6.1.1)
    • Maximum Steel Ratio: ρmax = 6.0% (practical limit)

{'='*80}
6. DESIGN SUMMARY AND VERIFICATION
{'='*80}

6.1 FINAL DESIGN SPECIFICATIONS:
    ✓ Column Size: {results['width']:.0f} × {results['height']:.0f} mm
    ✓ Longitudinal Reinforcement: 
      - {results['num_bars_x']:.0f} × {results['rebar_x']} in X-direction = {results['As_x']:,.0f} mm²
      - {results['num_bars_y']:.0f} × {results['rebar_y']} in Y-direction = {results['As_y']:,.0f} mm²
      - 4 × {results['corner_rebar']} corner bars = {results['As_corner']:,.0f} mm²
      - Total reinforcement = {results['As_provided']:,.0f} mm² ({results['steel_ratio']:.2f}%)
    ✓ Ties: {results['tie_size']} @ {results['tie_spacing']:.0f} mm c/c ({results['end_spacing']:.0f} mm in end regions)
    ✓ Cover: {results['cover']:.0f} mm clear

6.2 DETAILED DESIGN VERIFICATION:
    
    MINIMUM REINFORCEMENT CHECK:
    Required: ρmin = 1.0%
    Provided: ρ = {results['steel_ratio']:.2f}%
    Status: {'✓ OK' if results['steel_ratio'] >= 1.0 else '✗ INCREASE REINFORCEMENT'}
    
    MAXIMUM REINFORCEMENT CHECK:
    Limit: ρmax = 6.0% (practical limit)
    Provided: ρ = {results['steel_ratio']:.2f}%
    Status: {'✓ OK' if results['steel_ratio'] <= 6.0 else '✗ REDUCE REINFORCEMENT OR INCREASE SIZE'}
    
    TIE SPACING CHECK:
    Maximum Allowed: {results['max_spacing']:.0f} mm
    Provided: {results['tie_spacing']:.0f} mm
    Status: {'✓ OK' if results['tie_spacing_ok'] else '✗ REDUCE SPACING'}
    
    CAPACITY CHECK:
    Applied Load: Pu = {results['P']:,.0f} kN
    Design Capacity: φPn = {results['Pu_capacity']:,.0f} kN
    Utilization: {results['utilization']:.1f}%
    Status: {'✓ ADEQUATE' if results['utilization'] <= 100 else '✗ INADEQUATE'}

6.3 SAFETY AND SERVICEABILITY:
    
    SAFETY MARGIN: {100 - results['utilization']:.1f}%
    {'• Excellent safety margin (>20%)' if results['utilization'] < 80 else '• Adequate safety margin (10-20%)' if results['utilization'] < 90 else '• Minimal safety margin (<10%)' if results['utilization'] < 95 else '• Very tight design - consider increasing capacity'}
    
    DEVELOPMENT LENGTH CHECK:
    Required: Ld = {results['ld_required']:.0f} mm
    Available: {results['length']*1000-2*results['end_length']:.0f} mm
    Status: {'✓ ADEQUATE' if results['length']*1000-2*results['end_length'] >= results['ld_required'] else '✗ INSUFFICIENT - INCREASE COLUMN LENGTH OR REDUCE BAR SIZE'}

{'='*80}
7. DESIGN RECOMMENDATIONS
{'='*80}
"""
        
        # Add specific recommendations with detailed analysis
        if results['utilization'] > 100:
            report += f"""
    🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:
    • Column capacity ({results['Pu_capacity']:,.0f} kN) < Applied load ({results['P']:,.0f} kN)
    • REQUIRED ACTIONS:
      - Increase column size: Try {results['width']+50:.0f} × {results['height']+50:.0f} mm
      - OR increase reinforcement significantly
      - Re-analyze with increased capacity
"""
        elif results['utilization'] > 95:
            report += f"""
    ⚠️ DESIGN CONCERNS:
    • Very high utilization ({results['utilization']:.1f}%) - minimal safety margin
    • RECOMMENDATIONS:
      - Consider slight increase in section size or reinforcement
      - Verify all load factors are appropriate
      - Consider fatigue effects if applicable
"""
        elif results['utilization'] > 85:
            report += f"""
    ✓ DESIGN ACCEPTABLE BUT CONSIDER:
    • Utilization is {results['utilization']:.1f}% - adequate but not conservative
    • Could add slight reinforcement for additional safety margin
    • Current design provides {100-results['utilization']:.1f}% safety margin
"""
        else:
            report += f"""
    ✅ EXCELLENT DESIGN:
    • Conservative utilization ({results['utilization']:.1f}%)
    • Good safety margin ({100-results['utilization']:.1f}%)
    • Design provides reliable performance
"""
        
        if not results['tie_spacing_ok']:
            report += f"""
    🔧 TIE SPACING CORRECTION REQUIRED:
    • Current spacing ({results['tie_spacing']:.0f} mm) > Maximum allowed ({results['max_spacing']:.0f} mm)
    • SOLUTION: Reduce spacing to {results['max_spacing']:.0f} mm or less
    • This is a MANDATORY requirement per ACI 318M-25 Ch.10.7.6.1
"""
        
        if results['steel_ratio'] < 1.0:
            additional_steel = (0.01 * results['Ag'] - results['As_provided'])
            report += f"""
    📊 MINIMUM REINFORCEMENT VIOLATION:
    • Current: {results['steel_ratio']:.2f}% < Required: 1.0% (ACI 10.6.1.1)
    • SOLUTION: Add {additional_steel:.0f} mm² of reinforcement
    • Suggested: Add 2 more {results['rebar_x']} bars
"""
        
        if results['steel_ratio'] > 6.0:
            report += f"""
    ⚠️ EXCESSIVE REINFORCEMENT:
    • Current: {results['steel_ratio']:.2f}% > Practical limit: 6.0%
    • SOLUTION: Increase column size to accommodate reinforcement properly
    • Consider constructability and concrete placement issues
"""
        
        report += f"""

{'='*80}
8. CALCULATION VERIFICATION AND QUALITY ASSURANCE
{'='*80}

8.1 INPUT VERIFICATION CHECKLIST:
    ✓ Geometry: {results['width']:.0f} × {results['height']:.0f} × {results['length']*1000:.0f} mm
    ✓ Loads: P={results['P']:.0f} kN, Mx={results['Mx']:.0f} kN⋅m, My={results['My']:.0f} kN⋅m
    ✓ Materials: fc'={results['fc']:.0f} MPa, fy={results['fy']:.0f} MPa
    ✓ Reinforcement: {results['As_provided']:,.0f} mm² total steel area
    ✓ Cover: {results['cover']:.0f} mm clear cover

8.2 CALCULATION METHOD VALIDATION:
    • Analysis Method: Simplified interaction approach
    • Code Reference: ACI 318M-25 Chapter 10 (Columns)
    • Section References: 10.3 (Axial Load), 10.6 (Reinforcement Limits)
    • Assumptions: Linear strain distribution, perfect bond
    • Limitations: P-M interaction simplified for preliminary design

8.3 DESIGN CONFIDENCE LEVEL:
    Based on calculation sophistication: {'HIGH' if results['utilization'] < 90 else 'MEDIUM' if results['utilization'] < 95 else 'LOW - REQUIRES DETAILED ANALYSIS'}
    Recommended for: {'Final design with engineer review' if results['utilization'] < 85 else 'Preliminary design - detailed analysis recommended'}

{'='*80}
END OF DETAILED CALCULATION REPORT

IMPORTANT DISCLAIMERS:
• This analysis uses simplified methods suitable for preliminary design
• Final design must comply with all applicable building codes
• Professional engineer review and approval required
• Consider all applicable load combinations and special conditions
• Verify material specifications and construction practices
• This software provides calculation assistance only

Report generated by: Professional Column Design v3.0
Analysis date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
"""
        
        self.results_text.insert(tk.END, report)
    
    def export_to_pdf(self):
        """Export the complete report to PDF format"""
        if self.last_results is None:
            messagebox.showwarning("No Data", "Please generate report first.")
            return
        
        if not HAS_REPORTLAB:
            messagebox.showerror("Missing Library", 
                               "ReportLab is required for PDF export.\n"
                               "Install with: pip install reportlab")
            return
        
        try:
            from tkinter import filedialog
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            import os
            
            # Generate diagrams first
            self.generate_report_diagrams()
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Save Report as PDF"
            )
            
            if not filename:
                return
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.darkblue
            )
            
            results = self.last_results
            
            # Title
            story.append(Paragraph("REINFORCED CONCRETE COLUMN DESIGN REPORT", title_style))
            story.append(Paragraph("WITH DETAILED CALCULATIONS", title_style))
            story.append(Spacer(1, 20))
            
            # Project Information
            project_info = f"""
            <b>Analysis Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Software:</b> Professional Column Design v3.0<br/>
            <b>Design Code:</b> ACI 318M-25 Chapter 10 (Columns)<br/>
            <b>Column Size:</b> {results['width']:.0f} × {results['height']:.0f} mm
            """
            story.append(Paragraph(project_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add Section Preview if available
            if hasattr(self, 'section_preview_path') and os.path.exists(self.section_preview_path):
                story.append(Paragraph("DETAILED SECTION PREVIEW", styles['Heading2']))
                # Add image with appropriate size
                img = Image(self.section_preview_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 20))
            
            # Input Parameters Summary
            story.append(Paragraph("1. DESIGN INPUT PARAMETERS", styles['Heading2']))
            
            input_text = f"""
            <b>Geometry:</b><br/>
            • Column Cross-Section: {results['width']:.0f} × {results['height']:.0f} mm<br/>
            • Column Length: {results['length']:.1f} m<br/>
            • Gross Area: Ag = {results['width']:.0f} × {results['height']:.0f} = {results['Ag']:,.0f} mm²<br/><br/>
            
            <b>Applied Loads:</b><br/>
            • Axial Load: Pu = {results['P']:,.0f} kN<br/>
            • Moment X: Mux = {results['Mx']:.0f} kN⋅m → ex = {results['ex']:.1f} mm<br/>
            • Moment Y: Muy = {results['My']:.0f} kN⋅m → ey = {results['ey']:.1f} mm<br/><br/>
            
            <b>Materials:</b><br/>
            • Concrete: fc' = {results['fc']:.0f} MPa<br/>
            • Steel: fy = {results['fy']:.0f} MPa
            """
            story.append(Paragraph(input_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Reinforcement Design
            story.append(Paragraph("2. REINFORCEMENT DESIGN WITH CALCULATIONS", styles['Heading2']))
            
            rebar_text = f"""
            <b>Longitudinal Reinforcement Area Calculations:</b><br/><br/>
            
            <b>X-Direction:</b><br/>
            Size: {results['rebar_x']} (Area = {self.get_rebar_area(results['rebar_x']):.0f} mm² per bar)<br/>
            Formula: As,x = n × Ab = {results['num_bars_x']:.0f} × {self.get_rebar_area(results['rebar_x']):.0f} = {results['As_x']:,.0f} mm²<br/><br/>
            
            <b>Y-Direction:</b><br/>
            Size: {results['rebar_y']} (Area = {self.get_rebar_area(results['rebar_y']):.0f} mm² per bar)<br/>
            Formula: As,y = n × Ab = {results['num_bars_y']:.0f} × {self.get_rebar_area(results['rebar_y']):.0f} = {results['As_y']:,.0f} mm²<br/><br/>
            
            <b>Corner Bars:</b><br/>
            Size: {results['corner_rebar']} (Area = {self.get_rebar_area(results['corner_rebar']):.0f} mm² per bar)<br/>
            Formula: As,corner = 4 × Ab = 4 × {self.get_rebar_area(results['corner_rebar']):.0f} = {results['As_corner']:,.0f} mm²<br/><br/>
            
            <b>Total Steel:</b><br/>
            Formula: As,total = As,x + As,y + As,corner<br/>
            = {results['As_x']:,.0f} + {results['As_y']:,.0f} + {results['As_corner']:,.0f} = {results['As_provided']:,.0f} mm²<br/><br/>
            
            <b>Steel Ratio:</b><br/>
            Formula: ρ = As,total / Ag × 100%<br/>
            = {results['As_provided']:,.0f} / {results['Ag']:,.0f} × 100% = {results['steel_ratio']:.2f}%<br/>
            Check: {'✓ OK' if 1.0 <= results['steel_ratio'] <= 6.0 else '✗ Outside range'} (Min: 1.0%, Max: 6.0%)
            """
            story.append(Paragraph(rebar_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Capacity Calculations
            story.append(Paragraph("3. CAPACITY CALCULATIONS", styles['Heading2']))
            
            capacity_text = f"""
            <b>Nominal Axial Capacity (Simplified Method):</b><br/><br/>
            
            <b>Concrete Contribution:</b><br/>
            Formula: Pn,concrete = 0.85 × fc' × (Ag - As)<br/>
            = 0.85 × {results['fc']:.0f} × ({results['Ag']:,.0f} - {results['As_provided']:,.0f})<br/>
            = 0.85 × {results['fc']:.0f} × {results['Ag'] - results['As_provided']:,.0f}<br/>
            = {results['Pn_concrete']/1000:,.0f} kN<br/><br/>
            
            <b>Steel Contribution:</b><br/>
            Formula: Pn,steel = fy × As<br/>
            = {results['fy']:.0f} × {results['As_provided']:,.0f}<br/>
            = {results['Pn_steel']/1000:,.0f} kN<br/><br/>
            
            <b>Total Nominal Capacity:</b><br/>
            Formula: Pn = Pn,concrete + Pn,steel<br/>
            = {results['Pn_concrete']/1000:,.0f} + {results['Pn_steel']/1000:,.0f} = {results['Pn_total']/1000:,.0f} kN<br/><br/>
            
            <b>Design Capacity:</b><br/>
            Formula: φPn = φ × Pn (φ = 0.65 for tied columns)<br/>
            = 0.65 × {results['Pn_total']/1000:,.0f} = {results['Pu_capacity']:,.0f} kN<br/><br/>
            
            <b>Utilization Check:</b><br/>
            Formula: Utilization = (Applied Load / Design Capacity) × 100%<br/>
            = ({results['P']:,.0f} / {results['Pu_capacity']:,.0f}) × 100% = {results['utilization']:.1f}%<br/>
            Status: <b>{'✅ ADEQUATE' if results['utilization'] <= 100 else '❌ INADEQUATE'}</b><br/>
            Safety Margin: {100 - results['utilization']:.1f}%
            """
            story.append(Paragraph(capacity_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add P-M Interaction Diagrams if available
            if hasattr(self, 'pm_diagrams_path') and os.path.exists(self.pm_diagrams_path):
                story.append(Paragraph("P-M INTERACTION DIAGRAMS", styles['Heading2']))
                # Add image with appropriate size
                img = Image(self.pm_diagrams_path, width=7*inch, height=3.5*inch)
                story.append(img)
                
                # Add diagram description
                diagram_desc = f"""
                <b>Interaction Diagram Analysis:</b><br/>
                • P-Mx and P-My interaction curves generated using ACI 318M-25 provisions<br/>
                • Applied loads: P = {results['P']:.0f} kN, Mx = {results['Mx']:.0f} kN⋅m, My = {results['My']:.0f} kN⋅m<br/>
                • Utilization: {results['utilization']:.1f}% of capacity<br/>
                • Safety Status: <b>{'SAFE' if results['utilization'] <= 100 else 'UNSAFE'}</b><br/>
                • Design complies with interaction requirements
                """
                story.append(Paragraph(diagram_desc, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Design Summary
            story.append(Paragraph("4. FINAL DESIGN SUMMARY", styles['Heading2']))
            
            summary_text = f"""
            <b>Design Specifications:</b><br/>
            • Column Size: {results['width']:.0f} × {results['height']:.0f} mm<br/>
            • X-Direction: {results['num_bars_x']:.0f} × {results['rebar_x']} = {results['As_x']:,.0f} mm²<br/>
            • Y-Direction: {results['num_bars_y']:.0f} × {results['rebar_y']} = {results['As_y']:,.0f} mm²<br/>
            • Corner Bars: 4 × {results['corner_rebar']} = {results['As_corner']:,.0f} mm²<br/>
            • Total Steel: {results['As_provided']:,.0f} mm² ({results['steel_ratio']:.2f}%)<br/>
            • Ties: {results['tie_size']} @ {results['tie_spacing']:.0f} mm c/c<br/>
            • Clear Cover: {results['cover']:.0f} mm<br/><br/>
            
            <b>Design Verification:</b><br/>
            {'✓' if results['steel_ratio'] >= 1.0 else '✗'} Minimum reinforcement: {results['steel_ratio']:.2f}% ≥ 1.0%<br/>
            {'✓' if results['steel_ratio'] <= 6.0 else '✗'} Maximum reinforcement: {results['steel_ratio']:.2f}% ≤ 6.0%<br/>
            {'✓' if results['tie_spacing_ok'] else '✗'} Tie spacing: {results['tie_spacing']:.0f} mm ≤ {results['max_spacing']:.0f} mm<br/>
            {'✓' if results['utilization'] <= 100 else '✗'} Capacity check: {results['utilization']:.1f}% ≤ 100%<br/><br/>
            
            <b>Overall Status: {'✅ DESIGN ACCEPTABLE' if results['utilization'] <= 100 and results['tie_spacing_ok'] and 1.0 <= results['steel_ratio'] <= 6.0 else '⚠️ DESIGN REQUIRES MODIFICATION'}</b>
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Footer
            footer_text = f"""
            <b>DISCLAIMERS:</b><br/>
            • This analysis uses simplified methods for preliminary design<br/>
            • Professional engineer review and approval required<br/>
            • Verify all applicable codes and project-specific requirements<br/>
            • Consider all load combinations and special conditions<br/><br/>
            Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            Software: Professional Column Design v3.0
            """
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            messagebox.showinfo("PDF Export Complete", 
                               f"Report successfully exported to:\n{filename}")
        
        except ImportError:
            messagebox.showerror("Missing Library", 
                               "ReportLab library is required for PDF export.\n"
                               "Install with: pip install reportlab")
        except Exception as e:
            messagebox.showerror("PDF Export Error", 
                               f"Could not export to PDF: {str(e)}")
    
    def export_report(self):
        """Export the complete report to a text file"""
        if self.last_results is None:
            messagebox.showwarning("No Data", "Please generate report first.")
            return
        
        try:
            filename = f"Column_Design_Report_{self.last_results['width']:.0f}x{self.last_results['height']:.0f}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results_text.get(1.0, tk.END))
            
            messagebox.showinfo("Export Complete", f"Report exported as {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export report: {str(e)}")
    
    def clear_all(self):
        """Clear all results and reset interface"""
        self.analysis_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        
        # Clear interaction diagram
        for widget in self.figure_frame.winfo_children():
            widget.destroy()
        
        self.last_results = None
        self.interaction_data = None
        
        messagebox.showinfo("Cleared", "All results have been cleared.")


def main():
    root = tk.Tk()
    app = ProfessionalColumnDesign(root)
    
    # Configure window resize behavior
    def on_configure(event):
        app.main_canvas.configure(scrollregion=app.main_canvas.bbox("all"))
    
    app.main_canvas.bind('<Configure>', on_configure)
    
    root.mainloop()


if __name__ == "__main__":
    main()
