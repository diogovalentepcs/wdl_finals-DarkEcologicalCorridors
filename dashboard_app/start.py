# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 11:23:27 2021

@author: João Afonso
"""


import tkinter as tk
from tkinter.filedialog import askopenfilename
import os
from tkinter import simpledialog
from tkinter import ttk
from score import Score

class Start:
    def __init__(self, master):

        # Initialize master widget
        self.master = master 
        self.master.geometry('600x820')
        self.master.title("YODAS")
        self.master.configure(background='white')

        try:
            self.master.iconbitmap('yodas.ico')
        except:
            pass

        self.title_frame = tk.Frame(self.master, bg='#3C78D8')
        tk.Label(self.title_frame, text='OPTIMIZATION OF DARK CORRIDORS', font=('arial', 12, 'bold'), bg='#3C78D8', fg='white').pack(side='left', anchor='c', pady=15, expand=True)
        self.title_frame.pack(side='top', fill='x', expand=False)
        
        self.city_frame = tk.Frame(self.master, bg='white')
        self.city_frame.pack(anchor='w', pady=15)

        self.city_label = tk.Label(self.city_frame, text='City grid', bg='white', font=('arial', 9, 'bold'))
        self.city_label.pack(side='left', anchor='w', padx=10)

        self.grid_file_btn = tk.Button(self.city_frame, text='Choose file', command=self.ask_grid_file)
        self.grid_file_btn.pack(side='left', anchor='w', padx=10)

        self.name_city_btn = tk.Button(self.city_frame, text='Name city', command=self.name_city)
        self.name_city_btn.pack(side='left', anchor='w', padx=10)

        self.grid_path_label = tk.Label(self.city_frame, text='', bg='white', font=('arial', 8, 'underline'))
        self.grid_path_label.pack(side='left', anchor='w', padx=10)
        
        self.lights_frame = tk.Frame(self.master, bg='white')
        self.lights_frame.pack(anchor='w', pady=15)
        
        self.lights_label = tk.Label(self.lights_frame, text='Street lights', bg='white', font=('arial', 9, 'bold'))
        self.lights_label.pack(side='left', anchor='w', padx=10)

        self.lights_file_btn = tk.Button(self.lights_frame, text='Choose file', command=self.ask_lights_file)
        self.lights_file_btn.pack(side='left', anchor='w', padx=10)

        self.lights_path_label = tk.Label(self.lights_frame, text='', bg='white', font=('arial', 8, 'underline'))
        self.lights_path_label.pack(side='left', anchor='w', padx=10)        
        
        self.map_frame = tk.Frame(self.master, bg='white')
        self.map_frame.pack(anchor='w', pady=15)
        
        self.map_label = tk.Label(self.map_frame, text='City map', bg='white', font=('arial', 9, 'bold'))
        self.map_label.pack(side='left', anchor='w', padx=10)
        
        self.map_entry = tk.Entry(self.map_frame, width=70, font=('arial', 7, 'underline'))
        self.map_entry.pack(side='left', anchor='w', padx=10)
        self.map_entry.insert(0, 'https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E06000023.json')
        
        tk.Label(self.master, text='Animal-related features', bg='white', fg='#3C78D8', font=('arial', 11, 'bold')).pack(anchor='w', padx=10, pady=15)

        main_frame = tk.Frame(self.master, bg='white')
        main_frame.pack(anchor='w', padx=10)

        frame = tk.Frame(main_frame, bg='white')
        self.animal_canvas = tk.Canvas(frame, bg='white', width=550, height=150)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.animal_canvas.yview, background='white')
        self.animal_frame = tk.Frame(self.animal_canvas, bg='white')
        self.animal_frame.bind("<Configure>", lambda e: self.animal_canvas.configure(scrollregion=self.animal_canvas.bbox("all")))

        self.animal_frame.bind('<Enter>', lambda e: self._bound_to_mousewheel(e, self.animal_canvas))
        self.animal_frame.bind('<Leave>', lambda e: self._unbound_to_mousewheel(e, self.animal_canvas))

        self.animal_canvas.create_window((0, 0), window=self.animal_frame, anchor="nw")
        self.animal_canvas.configure(yscrollcommand=scrollbar.set)
        
        frame.pack()
        self.animal_canvas.pack(side="left", fill="none", expand=False)
        scrollbar.pack(side="right", fill="y")
        main_frame.pack()
        
        self.animal_features = dict()

        feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame = self.create_feature(0, 'animal')

        self.animal_features[0] = ['Feature', feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame, '']
        self.animal_features_idxs = [0]

        self.add_animal_feature_btn = tk.Button(self.master, text='Add animal feature', command=lambda: self.add_feature('animal'), font=('arial', 8, 'normal'))
        self.add_animal_feature_btn.pack(anchor='w', padx=10, pady=10)

        tk.Label(self.master, text='Human-related features', bg='white', fg='#3C78D8', font=('arial', 11, 'bold')).pack(anchor='w', padx=10, pady=15)

        main_frame = tk.Frame(self.master, bg='white')
        main_frame.pack(anchor='w', padx=10)

        frame = tk.Frame(main_frame, bg='white')
        self.human_canvas = tk.Canvas(frame, bg='white', width=550, height=150)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.human_canvas.yview, background='white')
        self.human_frame = tk.Frame(self.human_canvas, bg='white')
        self.human_frame.bind("<Configure>", lambda e: self.human_canvas.configure(scrollregion=self.human_canvas.bbox("all")))

        self.human_frame.bind('<Enter>', lambda e: self._bound_to_mousewheel(e, self.human_canvas))
        self.human_frame.bind('<Leave>', lambda e: self._unbound_to_mousewheel(e, self.human_canvas))

        self.human_canvas.create_window((0, 0), window=self.human_frame, anchor="nw")
        self.human_canvas.configure(yscrollcommand=scrollbar.set)
        
        frame.pack()
        self.human_canvas.pack(side="left", fill="none", expand=False)
        scrollbar.pack(side="right", fill="y")
        main_frame.pack()

        self.human_features = dict()
        
        feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame = self.create_feature(0, 'human')

        self.human_features[0] = ['Feature', feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame, '']
        self.human_features_idxs = [0]

        self.add_human_feature_btn = tk.Button(self.master, text='Add human feature', command=lambda: self.add_feature('human'), font=('arial', 8, 'normal'))
        self.add_human_feature_btn.pack(anchor='w', padx=10, pady=10)

        self.last_separator = ttk.Separator(self.master, orient='horizontal').pack(anchor='center', fill='x', padx=10, pady=5)

        self.next_button = tk.Button(self.master, text='Go to score calculation', command=self.next, font=('arial', 10, 'bold'))
        self.next_button.pack(anchor='w', padx=10, pady=5)
        
    # Bound a canvas to mouse wheel for scrolling
    def _bound_to_mousewheel(self, event, canvas):
        canvas.bind_all("<MouseWheel>", lambda e: self._scroll(e, canvas))

    # Unbound a canvas to a mouse wheel
    def _unbound_to_mousewheel(self, event, canvas):
        canvas.unbind_all("<MouseWheel>")

    # Scroll through a canvas (I think this only works with windows - needs ataptation for other OS)
    def _scroll(self, event, canvas):
        canvas.yview_scroll(-1*int((event.delta/120)), "units")

    def next(self):
        
        animal_feats = dict()
        for key in self.animal_features:
            animal_feats[key] = [self.animal_features[key][0], self.animal_features[key][-1]]

        human_feats = dict()
        for key in self.human_features:
            human_feats[key] = [self.human_features[key][0], self.human_features[key][-1]]

        root2 = tk.Toplevel()
        Score(root2, self.map_entry.get(), self.grid_filename, self.lights_filename, animal_feats, human_feats)
        root2.mainloop()

    def ask_grid_file(self):
        self.grid_filename = askopenfilename(filetypes=(("CSV file", "*.csv"),))
        self.grid_path_label.configure(text=os.path.basename(self.grid_filename))
        
    def ask_lights_file(self):
        self.lights_filename = askopenfilename(filetypes=(("CSV file", "*.csv"),))
        self.lights_path_label.configure(text=os.path.basename(self.lights_filename))

    def name_city(self):
        
        city = simpledialog.askstring(title="City", prompt="What is the city name? (Up to 10 characters) ")
        
        if city == '' or city is None:
            return
        
        self.city_label.configure(text=city)
        self.name_city_btn.configure(text='Rename city')

    def ask_feature_file(self, type, idx):

        filename = askopenfilename(filetypes=(("CSV file", "*.csv"),))

        if type == 'animal':
            self.animal_features[idx][-1] = filename
            self.animal_features[idx][4].configure(text=os.path.basename(filename))
        else:
            self.human_features[idx][-1] = filename
            self.human_features[idx][4].configure(text=os.path.basename(filename))

    def rename_feature(self, type, idx):

        name = simpledialog.askstring(title="Feature", prompt="What is the feature name? (Up to 10 characters)")
        
        if name == '' or name is None:
            return
        
        if len(name) >= 10:
            name = name[:10]
            name_txt = name
        else:
            name_txt = name + ' '*(19-len(name))

        if type == 'animal':
            self.animal_features[idx][1].configure(text=name_txt)
            self.animal_features[idx][0] = name
        else:
            self.human_features[idx][1].configure(text=name_txt)
            self.human_features[idx][0] = name

    def create_feature(self, idx, type):
        
        if type == 'animal':
            feature_frame = tk.Frame(self.animal_frame, bg='white')
        
        else:
            feature_frame = tk.Frame(self.human_frame, bg='white')
        
        feature_frame.pack(anchor='w', pady=5)
            
        feature_label = tk.Label(feature_frame, text='Feature       ', bg='white', font=('arial', 9, 'bold'))
        feature_label.pack(side='left', anchor='w', padx=5)

        feat_file_btn = tk.Button(feature_frame, text='Choose file', font=('arial', 9, 'normal'), command=lambda: self.ask_feature_file(type, idx))
        feat_file_btn.pack(side='left', anchor='w', padx=5)

        name_feat_btn = tk.Button(feature_frame, text='Rename', font=('arial', 9, 'normal'), command=lambda: self.rename_feature(type, idx))
        name_feat_btn.pack(side='left', anchor='w', padx=5)
        
        del_feat_btn = tk.Button(feature_frame, text=' X ', font=('arial', 9, 'bold'), fg='black', bg='#ea9999', command=lambda: self.delete_feature(type, idx))
        del_feat_btn.pack(side='left', anchor='w', padx=5)

        feat_path_label = tk.Label(feature_frame, text='', bg='white', font=('arial', 9, 'underline'))
        feat_path_label.pack(side='left', anchor='w', padx=5)
        
        return feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame
    
    def delete_feature(self, type, idx):

        if type == 'animal':
            
            if len(self.animal_features) == 1:
                return
            
            for widget in self.animal_features[idx][1:-1]:
                widget.destroy()
                
            self.animal_features.pop(idx)
            self.animal_features_idxs.remove(idx)
        else:
            
            if len(self.human_features) == 1:
                return
            
            for widget in self.human_features[idx][1:-1]:
                widget.destroy()
                
            self.human_features.pop(idx)
            self.human_features_idxs.remove(idx)


    def add_feature(self, type):

        if type == 'animal':

            last_idx = self.animal_features_idxs[-1]

            feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame = self.create_feature(last_idx+1, type)

            self.animal_features[last_idx+1] = ['Feature', feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame, '']
            self.animal_features_idxs.append(last_idx+1)  
            
        else:


            last_idx = self.human_features_idxs[-1]

            feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame = self.create_feature(last_idx+1, type)

            self.human_features[last_idx+1] = ['Feature', feature_label, feat_file_btn, name_feat_btn, feat_path_label, del_feat_btn, feature_frame, '']
            self.human_features_idxs.append(last_idx+1)     


def main():

    root = tk.Tk()
    Start(root)
    root.mainloop()

if __name__ == '__main__':
    
    main()