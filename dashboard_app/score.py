# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 11:23:27 2021

@author: João Afonso
"""


import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from optimization import OPT
from matplotlib import rcParams
from shapely import wkt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

rcParams['figure.figsize'] = 32, 16
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['lines.linewidth'] = 2.

class Score:
    def __init__(self, master, city_map, grid_file, street_lights_file, animal_features, human_features):

        # Initialize master widget
        self.master = master 
        self.master.geometry('1500x800')
        self.master.title("YODAS")
        self.master.configure(background='white')
        self.master.state('zoomed')

        self.animal_features = animal_features
        self.human_features = human_features

        try:
            self.master.iconbitmap('yodas.ico')
        except:
            pass

        self.grid = pd.read_csv(grid_file)

        self.grid['geometry'] = self.grid['geometry'].apply(wkt.loads)
        self.grid = gpd.GeoDataFrame(self.grid, crs='EPSG:27700')

        self.title_frame = tk.Frame(self.master, bg='#3C78D8')
        tk.Label(self.title_frame, text='Optimization of dark corridors', font=('arial', 20, 'bold'), bg='#3C78D8', fg='white').pack(side='left', anchor='c', pady=30, expand=True)
        self.title_frame.pack(side='top', fill='x', expand=False)
        
        self.animal_frame = tk.Frame(self.master, bg='white')
        self.animal_frame.pack(side='left', expand=True, fill='y')
        
        self.middle_frame = tk.Frame(self.master, bg='white')
        self.middle_frame.pack(side='left', expand=True)
        
        self.human_frame = tk.Frame(self.master, bg='white')
        self.human_frame.pack(side='left', expand=True, fill='y')
        
        tk.Label(self.animal_frame, text='Animal score', font=('arial', 14, 'bold'), bg='white', fg='black').pack(anchor='n', pady=20) 
        
        self.animal_coefs = dict()
        
        main_frame = tk.Frame(self.animal_frame, bg='white')
        main_frame.pack(anchor='c', padx=10)

        frame = tk.Frame(main_frame, bg='white')
        self.animal_canvas = tk.Canvas(frame, bg='white', width=470, height=150)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.animal_canvas.yview, background='white')
        self.animal_features_frame = tk.Frame(self.animal_canvas, bg='white')
        self.animal_features_frame.bind("<Configure>", lambda e: self.animal_canvas.configure(scrollregion=self.animal_canvas.bbox("all")))

        self.animal_features_frame.bind('<Enter>', lambda e: self._bound_to_mousewheel(e, self.animal_canvas))
        self.animal_features_frame.bind('<Leave>', lambda e: self._unbound_to_mousewheel(e, self.animal_canvas))

        self.animal_canvas.create_window((0, 0), window=self.animal_features_frame, anchor="nw")
        self.animal_canvas.configure(yscrollcommand=scrollbar.set)
        
        frame.pack()
        self.animal_canvas.pack(side="left", fill="none", expand=False)
        scrollbar.pack(side="right", fill="y")
        main_frame.pack()

        r=0
        limit_r = 1
        c=-1
        for i, feat in enumerate(self.animal_features.keys()):
            c+=1
            tk.Label(self.animal_features_frame, text=self.animal_features[feat][0], bg='white').grid(column=c, row=r, ipadx=15, ipady=5)
            c+=1
            ent = tk.Entry(self.animal_features_frame, width=5, justify='center')
            ent.grid(column=c, row=r)
            self.animal_coefs[feat] = ent
            if i > limit_r:
                r+=1
                limit_r += 3
                c=-1

        self.animal_plot_frame = tk.Frame(self.animal_frame, bg='white')
        self.animal_plot_frame.pack(anchor = "c")

        figure1 = plt.Figure(figsize=(7,6), dpi=100)
        ax1 = figure1.add_subplot(111)
        self.animal_plot = FigureCanvasTkAgg(figure1, self.animal_plot_frame)
        self.animal_plot.get_tk_widget().pack(anchor = "c")
        self.grid.plot(color='grey', ax=ax1)
        figure1.tight_layout()
        ax1.set_axis_off()
        plt.close('all')

        self.btn_animal_frame = tk.Frame(self.animal_frame, bg='white')
        self.btn_animal_frame.pack(anchor = "c")
        
        self.animal_score_btn = tk.Button(self.btn_animal_frame, text='Compute score', font=('arial', 12, 'normal'), command=lambda: self.get_score('animal'))
        self.animal_score_btn.pack(side='left', anchor = "center", padx=10)
        
        self.animal_clean_btn = tk.Button(self.btn_animal_frame, text='Clear', font=('arial', 12, 'normal'), command=lambda: self.clear('animal'))
        self.animal_clean_btn.pack(side='left', anchor = "center", padx=10)
        
        self.save_btn = tk.Button(self.middle_frame, text='Save scores', font=('arial', 12, 'bold'), command=self.save_scores)
        self.save_btn.pack(anchor = "s", expand=True, fill='y')   
        
        self.opt_btn = tk.Button(self.middle_frame, text='Go to optimization', font=('arial', 12, 'bold'), command=self.optimization)
        self.opt_btn.pack(anchor = "s", expand=True, fill='y', pady=20)   
        
        tk.Label(self.human_frame, text='Human score', font=('arial', 14, 'bold'), bg='white', fg='black').pack(anchor='n', pady=20) 
        
        self.human_coefs = dict()
        
        main_frame = tk.Frame(self.human_frame, bg='white')
        main_frame.pack(anchor='c', padx=10)

        frame = tk.Frame(main_frame, bg='white')
        self.human_canvas = tk.Canvas(frame, bg='white', width=470, height=150)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.human_canvas.yview, background='white')
        self.human_features_frame = tk.Frame(self.human_canvas, bg='white')
        self.human_features_frame.bind("<Configure>", lambda e: self.human_canvas.configure(scrollregion=self.human_canvas.bbox("all")))

        self.human_features_frame.bind('<Enter>', lambda e: self._bound_to_mousewheel(e, self.human_canvas))
        self.human_features_frame.bind('<Leave>', lambda e: self._unbound_to_mousewheel(e, self.human_canvas))

        self.human_canvas.create_window((0, 0), window=self.human_features_frame, anchor="nw")
        self.human_canvas.configure(yscrollcommand=scrollbar.set)
        
        frame.pack()
        self.human_canvas.pack(side="left", fill="none", expand=False)
        scrollbar.pack(side="right", fill="y")
        main_frame.pack()
        
        r=0
        limit_r = 1
        c=-1
        for i, feat in enumerate(self.human_features.keys()):
            c+=1
            tk.Label(self.human_features_frame, text=self.human_features[feat][0], bg='white').grid(column=c, row=r, ipadx=15, ipady=5)
            c+=1
            ent = tk.Entry(self.human_features_frame, width=5, justify='center')
            ent.grid(column=c, row=r)
            self.human_coefs[feat] = ent
            if i > limit_r:
                r+=1
                limit_r += 3
                c=-1
                
        self.human_plot_frame = tk.Frame(self.human_frame, bg='white')
        self.human_plot_frame.pack(anchor = "c")
        
        figure2 = plt.Figure(figsize=(7,6), dpi=100)
        ax1 = figure2.add_subplot(111)
        self.human_plot = FigureCanvasTkAgg(figure2, self.human_plot_frame)
        self.human_plot.get_tk_widget().pack(anchor = "c")
        self.grid.plot(color='grey', ax=ax1)
        ax1.set_axis_off()
        figure2.tight_layout()
        plt.close('all')
        
        self.btn_human_frame = tk.Frame(self.human_frame, bg='white')
        self.btn_human_frame.pack(anchor = "c")
        
        self.human_score_btn = tk.Button(self.btn_human_frame, text='Compute score', font=('arial', 12, 'normal'), command=lambda: self.get_score('human'))
        self.human_score_btn.pack(side='left', anchor = "center", padx=10)
        
        self.human_clean_btn = tk.Button(self.btn_human_frame, text='Clear', font=('arial', 12, 'normal'), command=lambda: self.clear('human'))
        self.human_clean_btn.pack(side='left', anchor = "center", padx=10)
        
        self.grid_animal_score = None
        self.grid_human_score = None

    # Bound a canvas to mouse wheel for scrolling
    def _bound_to_mousewheel(self, event, canvas):
        canvas.bind_all("<MouseWheel>", lambda e: self._scroll(e, canvas))

    # Unbound a canvas to a mouse wheel
    def _unbound_to_mousewheel(self, event, canvas):
        canvas.unbind_all("<MouseWheel>")
        
    def optimization(self):
        
        if self.grid_animal_score is None or self.grid_human_score is None:
            messagebox.showerror('Error', 'Please compute the final scores before doing the optimization.')
        else:
            root2 = tk.Toplevel()
            OPT(root2)
            root2.mainloop()
    
    def clear(self, what):
        
        if what == 'human':
            
            for entry in self.human_coefs.values():
                entry.delete(0, 'end')
                
            self.human_plot.get_tk_widget().destroy()
            
            figure1 = plt.Figure(figsize=(7,6), dpi=100)
            ax1 = figure1.add_subplot(111)
            self.human_plot = FigureCanvasTkAgg(figure1, self.human_plot_frame)
            self.human_plot.get_tk_widget().pack(anchor = "c")
            self.grid.plot(color='grey', ax=ax1)
            ax1.set_axis_off()
            plt.close('all')

        else:
            
            for entry in self.animal_coefs.values():
                entry.delete(0, 'end')
            
            self.animal_plot.get_tk_widget().destroy()
            
            figure1 = plt.Figure(figsize=(7,6), dpi=100)
            ax1 = figure1.add_subplot(111)
            self.animal_plot = FigureCanvasTkAgg(figure1, self.animal_plot_frame)
            self.animal_plot.get_tk_widget().pack(anchor = "c")
            self.grid.plot(color='grey', ax=ax1)
            ax1.set_axis_off()
            plt.close('all')
    
        self.grid_animal_score = None
        self.grid_human_score = None

        self.master.update_idletasks()
      
    
    def get_score(self, what):
        
        if what == 'human':
            
            self.grid_human_score = self.grid.copy()
        
            coefs = dict()
            
            for key in self.human_coefs:
                coefs[key] = float(self.human_coefs[key].get())
                feat_df = pd.read_csv(self.human_features[key][1])
                if 'geometry' in feat_df.columns.tolist():
                    feat_df = feat_df.drop(columns=['geometry'])
                feat_col = [c for c in feat_df if c != 'zone'][0]
                x = feat_df[feat_col].to_numpy().reshape(-1, 1)
                scaler = MinMaxScaler()
                x = scaler.fit_transform(x)
                feat_df[key] = x
                feat_df = feat_df.drop(columns=[feat_col])
                self.grid_human_score = self.grid_human_score.merge(feat_df, on='zone')
                
            #self.grid.to_csv('test_grid.csv', index=False)
                
            self.grid_human_score['human_score_unscaled'] = 0
            for key in self.human_coefs:
                self.grid_human_score['human_score_unscaled'] = self.grid_human_score['human_score_unscaled'] + coefs[key]*self.grid_human_score[key]
                
            x = self.grid_human_score['human_score_unscaled'].to_numpy().reshape(-1, 1)
            scaler = MinMaxScaler()
            x = scaler.fit_transform(x)
            
            self.grid_human_score['human_score'] = x
            
            self.grid_human_score = self.grid_human_score.drop(columns=['human_score_unscaled'])
                
            self.human_plot.get_tk_widget().destroy()
            
            figure1 = plt.Figure(figsize=(7,6), dpi=100)
            ax1 = figure1.add_subplot(111)
            self.human_plot = FigureCanvasTkAgg(figure1, self.human_plot_frame)
            self.human_plot.get_tk_widget().pack(anchor = "c")
            self.grid_human_score.plot('human_score', ax=ax1)
            ax1.set_axis_off()
            figure1.tight_layout()
            plt.close('all')
            
        else:
            
            self.grid_animal_score = self.grid.copy()
        
            coefs = dict()
            
            for key in self.animal_coefs:
                coefs[key] = float(self.animal_coefs[key].get())
                feat_df = pd.read_csv(self.animal_features[key][1])
                if 'geometry' in feat_df.columns.tolist():
                    feat_df = feat_df.drop(columns=['geometry'])
                feat_col = [c for c in feat_df if c != 'zone'][0]
                x = feat_df[feat_col].to_numpy().reshape(-1, 1)
                scaler = MinMaxScaler()
                x = scaler.fit_transform(x)
                feat_df[key] = x
                feat_df = feat_df.drop(columns=[feat_col])
                self.grid_animal_score = self.grid_animal_score.merge(feat_df, on='zone')
                
            #self.grid.to_csv('test_grid.csv', index=False)
                
            self.grid_animal_score['animal_score_unscaled'] = 0
            for key in self.animal_coefs:
                self.grid_animal_score['animal_score_unscaled'] = self.grid_animal_score['animal_score_unscaled'] + coefs[key]*self.grid_animal_score[key]
            
            x = self.grid_animal_score['animal_score_unscaled'].to_numpy().reshape(-1, 1)
            scaler = MinMaxScaler()
            x = scaler.fit_transform(x)
            
            self.grid_animal_score['animal_score'] = x
            
            self.grid_animal_score = self.grid_animal_score.drop(columns=['animal_score_unscaled'])
                
            self.animal_plot.get_tk_widget().destroy()
            
            figure1 = plt.Figure(figsize=(7,6), dpi=100)
            ax1 = figure1.add_subplot(111)
            self.animal_plot = FigureCanvasTkAgg(figure1, self.animal_plot_frame)
            self.animal_plot.get_tk_widget().pack(anchor = "c")
            self.grid_animal_score.plot('animal_score', ax=ax1)
            ax1.set_axis_off()
            figure1.tight_layout()
            plt.close('all')
            
        self.master.update_idletasks()
        
    def save_scores(self):
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        path = askdirectory()
        self.grid_animal_score.to_csv(path + f'/animal_score_{now}.csv', index=False)
        self.grid_human_score.to_csv(path + f'/human_score_{now}.csv', index=False)
        
        messagebox.showinfo('Save scores', 'Score files saved successfully.')
        
        
def main():
    
    dict_animal = {0: ['Num_Prey', 'data/num_preys.csv'], 1: ['Dist_Water', 'data/dist_nearest_water_bodies.csv'], 2: ['Dist_Habitats', 'data/dist_nearest_wildlife_corridors.csv'], 3: ['Dist_Green', 'data/dist_nearest_green_alleys.csv']}
    dict_human = {0: ['Population', 'data/population.csv'], 1: ['Car_Flows', 'data/flows.csv'], 2: ['Dist_Bus', 'data/dist_bus.csv'], 3: ['Num_Bus', 'data/count_bus.csv']}

    root = tk.Tk()
    Score(root, 'https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E06000023.json', 'data/grid.csv', 'data/streetlights.csv', dict_animal, dict_human)
    root.mainloop()

if __name__ == '__main__':
    
    main()