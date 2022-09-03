# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 11:23:27 2021

@author: João Afonso
"""


import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from YODAS.DarkCorridors import LightManager
from shapely import wkt
from threading import Thread
from datetime import datetime
from tkinter.filedialog import askdirectory, askopenfilename

plt.ioff()


class OPT:
    def __init__(self, master, city_map_file, street_lights_file, grid_df_with_scores):

        # Initialize master widget
        self.master = master 
        self.master.geometry('1500x800')
        self.master.title("YODAS")
        self.master.configure(background='white')
        self.master.state('zoomed')

        try:
            self.master.iconbitmap('yodas.ico')
        except:
            pass
        
        self.grid = grid_df_with_scores
        self.city_map_file = city_map_file
        self.street_lights_file = street_lights_file
        
        self.read_lights_and_map()

        self.title_frame = tk.Frame(self.master, bg='#3C78D8')
        self.title_frame.pack(side='top', fill='x', expand=False)
        
        tk.Label(self.title_frame, text='', font=('arial', 10, 'bold'), bg='#3C78D8', fg='white').pack(side='top', anchor='c', pady=5, expand=True)
        tk.Label(self.title_frame, text='Optimization of dark corridors', font=('arial', 20, 'bold'), bg='#3C78D8', fg='white').pack(side='top', anchor='c', pady=0, expand=True)
        
        self.state_label = tk.Label(self.title_frame, text='Opening grid and light data ...', font=('arial', 12, 'normal'), bg='#3C78D8', fg='#b1c9ef')
        self.state_label.pack(anchor='c', pady=15, expand=True)

        
        self.save_btn = tk.Button(self.master, text='Save results', command=self.save_results, state='disabled')
        self.save_btn.pack(anchor='c', pady=15)

        self.plot_frame = tk.Frame(self.master, bg='white')
        self.plot_frame.pack(anchor = "c")

        self.plot_lights_and_grid()

        
    def read_lights_and_map(self):
        
        self.streetlights = pd.read_csv(self.street_lights_file)
        if 'Unnamed: 0' in self.streetlights.columns:
          self.streetlights.rename(columns = {'Unnamed: 0': 'ID'}, inplace = True)
        elif 'ID' in self.streetlights.columns:
          pass
        else:
          raise Exception('Invalid street lights file!')

        self.streetlights['geometry'] = self.streetlights['geometry'].apply(wkt.loads)
        self.streetlights_gdf = gpd.GeoDataFrame(self.streetlights, crs='EPSG:27700')
        
        self.map = gpd.read_file(self.city_map_file)
        self.map = self.map.set_crs('EPSG:4326').to_crs('EPSG:27700')
        

    def plot_lights_and_grid(self):
        
        fig, axs = plt.subplots(1,2, figsize = (15, 15), sharex = True)

        # Original Lighting
        self.map.plot(color='#0A0E42', ax=axs[0])
        self.streetlights_gdf.plot(markersize=0.5, ax=axs[0], color='gold', alpha=0.5)
        axs[0].set_axis_off()
        axs[0].title.set_text('Original Lighting')

        #axs[1].set_aspect('equal')
        self.grid.geometry.plot(ax=axs[1], color='white', edgecolor='grey')
        axs[1].set_axis_off()
        axs[1].title.set_text('Grid')
        
        self.plot = FigureCanvasTkAgg(fig, self.plot_frame)
        self.plot.get_tk_widget().pack(anchor = "c")
        fig.tight_layout(pad=5)
        plt.close('all')        
        
        self.master.update_idletasks()
        
        th = Thread(target=self.run)
        th.start()

    def run(self):
        
        self.state_label.configure(text='Configuring YODAS LightManager ...')
        self.master.update_idletasks()
        
        manager = LightManager(self.grid, self.city_map_file, self.street_lights_file)
        
        self.state_label.configure(text='Plotting clusters ...')
        self.master.update_idletasks()
        
        fig = manager.plot_clusters()
        
        self.plot.get_tk_widget().destroy()
        
        self.plot = FigureCanvasTkAgg(fig, self.plot_frame)
        self.plot.get_tk_widget().pack(anchor = "c")
        plt.close('all')        

        self.master.update_idletasks()
        
        res = messagebox.askquestion('Cost matrix', 'Use the default cost matrix?')
        if res == 'yes':
            self.state_label.configure(text='Loading default cost matrix ...')
            self.master.update_idletasks()
            manager.load_cost_matrix('data/cost_matrix.csv')
        else:
            res = messagebox.askquestion('Cost matrix', 'Import cost matrix file?')
            if res == 'yes':
                filename = askopenfilename(filetypes=(("CSV file", "*.csv"),))
                if filename == '':
                    self.state_label.configure(text='Loading default cost matrix ...')
                    self.master.update_idletasks()
                    manager.load_cost_matrix(filename)
                else:
                    self.state_label.configure(text='Loading cost matrix ...')
                    self.master.update_idletasks()
                    manager.load_cost_matrix('data/cost_matrix.csv')                    
            else:
                res = messagebox.askquestion('Cost matrix', 'Creating a cost matrix from scratch will take a lot of time. Are you sure you want to create it? You will be asked to choose a local directory to save the new cost matrix.')
                if res == 'yes':
                    path = askdirectory()
                    now = datetime.now().strftime('%Y%m%d%H%M%S')
                    self.state_label.configure(text='Building cost matrix ...')
                    self.master.update_idletasks()
                    manager.build_cost_matrix(path + f'/cost_matrix_{now}.csv')
                else:
                    self.state_label.configure(text='Loading default cost matrix ...')
                    self.master.update_idletasks()
                    messagebox.showinfo('Cost matrix', 'Will load default cost matrix.')
                    manager.load_cost_matrix('data/cost_matrix.csv')
                
        self.state_label.configure(text='Finding possible paths ...')
        self.master.update_idletasks()
        
        manager.find_cluster_paths()
        fig = manager.plot_paths()
        
        self.plot.get_tk_widget().destroy()
        
        self.plot = FigureCanvasTkAgg(fig, self.plot_frame)
        self.plot.get_tk_widget().pack(anchor = "c")
        plt.close('all')        

        self.master.update_idletasks()
        
        self.state_label.configure(text='Optimizing paths to create dark corridors ...')
        self.master.update_idletasks()
        
        manager.create_dark_corridors()
        
        self.state_label.configure(text='Plotting dark corridors ...')
        self.master.update_idletasks()       
        
        self.new_lights, self.final_fig = manager.update_lighting()
        
        self.plot.get_tk_widget().destroy()
        
        self.plot = FigureCanvasTkAgg(self.final_fig, self.plot_frame)
        self.plot.get_tk_widget().pack(anchor = "c")
        plt.close('all')        

        self.master.update_idletasks()
        
        self.state_label.configure(text='Optimization done!')

        self.save_btn.configure(state='active')

        self.master.update_idletasks()    
        
    
    def save_results(self):
        
        path = askdirectory()
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        self.new_lights.to_csv(path + f'/new_lights_{now}.csv', index=False)
        self.final_fig.savefig(path + f'/new_lights_{now}.png')
        
        messagebox.showinfo('Save results', 'Files saved successfully.')
        
        res = messagebox.askquestion('Exit', 'Do you want to exit the optimization page?')
        if res == 'yes':
            self.master.destroy()
        
        
def main():
    
    optimization_df = pd.read_csv('data/grid.csv')
    optimization_df.geometry = gpd.GeoSeries.from_wkt(optimization_df.geometry)
    optimization_df = gpd.GeoDataFrame(optimization_df, geometry='geometry')

    root = tk.Tk()
    OPT(root, 'https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E06000023.json', 'data/streetlights.csv', optimization_df)
    root.mainloop()

if __name__ == '__main__':
    
    main()