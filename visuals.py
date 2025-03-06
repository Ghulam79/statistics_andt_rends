import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class DiabetesDashboard:
    def __init__(self, master, df):
        self.master = master
        self.df = df
        self.current_filters = {}
        
        # Configure main window
        self.master.title("Diabetes Analysis Dashboard")
        self.master.geometry("1400x1000")
        self.master.minsize(1200, 800)
        
        # Create main container
        self.main_panel = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel
        self.control_frame = ttk.Frame(self.main_panel, width=200)
        self.main_panel.add(self.control_frame)
        
        # Create visualization panel
        self.viz_frame = ttk.Frame(self.main_panel)
        self.main_panel.add(self.viz_frame)
        
        # Initialize components
        self._create_controls()
        self._create_visualizations()
        self._update_plots()
        
    def _create_controls(self):
        """Create control widgets"""
        control_header = ttk.Label(self.control_frame, text="Dashboard Controls", font=('Arial', 12, 'bold'))
        control_header.pack(pady=10)
        
        # Outcome filter
        self.outcome_var = tk.StringVar(value='All')
        outcome_frame = ttk.LabelFrame(self.control_frame, text="Filter by Outcome")
        outcome_frame.pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Radiobutton(outcome_frame, text="All Cases", variable=self.outcome_var, value='All', command=self._update_plots).pack(anchor=tk.W)
        ttk.Radiobutton(outcome_frame, text="Diabetes", variable=self.outcome_var, value='1', command=self._update_plots).pack(anchor=tk.W)
        ttk.Radiobutton(outcome_frame, text="No Diabetes", variable=self.outcome_var, value='0', command=self._update_plots).pack(anchor=tk.W)
        
        # Variable selection
        self.x_var = tk.StringVar(value='Glucose')
        self.y_var = tk.StringVar(value='BMI')
        
        var_frame = ttk.LabelFrame(self.control_frame, text="Plot Variables")
        var_frame.pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Label(var_frame, text="X-axis Variable:").pack(anchor=tk.W)
        x_dropdown = ttk.Combobox(var_frame, textvariable=self.x_var, 
                                 values=list(self.df.columns), state='readonly')
        x_dropdown.pack(fill=tk.X)
        
        ttk.Label(var_frame, text="Y-axis Variable:").pack(anchor=tk.W, pady=(5,0))
        y_dropdown = ttk.Combobox(var_frame, textvariable=self.y_var, 
                                 values=list(self.df.columns), state='readonly')
        y_dropdown.pack(fill=tk.X)
        
        # Update button
        ttk.Button(self.control_frame, text="Update Plots", command=self._update_plots).pack(pady=10)
        
    def _create_visualizations(self):
        """Create visualization containers"""
        # Configure grid layout
        self.viz_frame.columnconfigure(0, weight=1)
        self.viz_frame.columnconfigure(1, weight=1)
        self.viz_frame.rowconfigure(0, weight=1)
        self.viz_frame.rowconfigure(1, weight=1)
        
        # Scatter plot
        self.scatter_frame = ttk.Frame(self.viz_frame)
        self.scatter_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Histogram
        self.hist_frame = ttk.Frame(self.viz_frame)
        self.hist_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Heatmap
        self.heatmap_frame = ttk.Frame(self.viz_frame)
        self.heatmap_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
    def _update_plots(self):
        """Update all visualizations based on current filters"""
        filtered_df = self._apply_filters()
        self._draw_scatter_plot(filtered_df)
        self._draw_histogram(filtered_df)
        self._draw_heatmap(filtered_df)
        
    def _apply_filters(self):
        """Apply current filters to dataset"""
        df = self.df.copy()
        outcome_filter = self.outcome_var.get()
        
        if outcome_filter != 'All':
            df = df[df['Outcome'] == int(outcome_filter)]
            
        return df
    
    def _draw_scatter_plot(self, df):
        """Create/update scatter plot"""
        plt.close('all')  # Close previous figures
        fig = plt.Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        sns.scatterplot(
            data=df,
            x=self.x_var.get(),
            y=self.y_var.get(),
            hue='Outcome',
            palette='viridis',
            alpha=0.7,
            ax=ax
        )
        ax.set_title(f"{self.y_var.get()} vs {self.x_var.get()}")
        self._embed_plot(fig, self.scatter_frame)
        
    def _draw_histogram(self, df):
        """Create/update histogram"""
        fig = plt.Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        sns.histplot(
            data=df,
            x='Age',
            hue='Outcome',
            kde=True,
            palette='coolwarm',
            bins=15,
            ax=ax
        )
        ax.set_title("Age Distribution")
        self._embed_plot(fig, self.hist_frame)
        
    def _draw_heatmap(self, df):
        """Create/update heatmap"""
        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        corr_matrix = df[['Glucose', 'BMI', 'Age', 'Outcome']].corr()
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap='coolwarm',
            fmt=".2f",
            linewidths=0.5,
            ax=ax
        )
        ax.set_title("Correlation Heatmap")
        self._embed_plot(fig, self.heatmap_frame)
        
    def _embed_plot(self, fig, frame):
        """Embed matplotlib figure in Tkinter frame"""
        for widget in frame.winfo_children():
            widget.destroy()
            
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self._load_data()
        
    def _load_data(self):
        """Load and preprocess data"""
        try:
            df = pd.read_csv(self.file_path)
            df = df.dropna().drop_duplicates()
            print("Data loaded successfully")
            return df
        except Exception as e:
            raise RuntimeError(f"Data loading error: {str(e)}")

if __name__ == "__main__":
    # Load data
    loader = DataLoader('diabetes_dataset.csv')
    
    # Create GUI
    root = tk.Tk()
    dashboard = DiabetesDashboard(root, loader.df)
    root.mainloop()