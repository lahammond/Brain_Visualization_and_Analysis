# brainrender script for plotting cells from BrainJ 

# Author: 	Luke Hammond
# Cellular Imaging | Zuckerman Institute, Columbia University
# Date:	1st October, 2021

import numpy as np

import brainrender
from brainrender import Scene
from brainrender.actors import Points, PointsDensity


from rich import print
from myterial import orange
from pathlib import Path

# Import Pandas to read in csv
import pandas as pd

print(f"[{orange}]Running example: {Path(__file__).name}")

#Path to csv file containing cell locations - can load multiple cell files and plot together
cellsfile = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/BrainJ/C1_Detected_Cells.csv"
cellsfile2 = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/BrainJ/C2_Detected_Cells.csv"


#Modify Settings
brainrender.settings.WHOLE_SCREEN = False  # make the rendering window smaller - full screen required for animations
brainrender.settings.SHOW_AXES = False #show/hide axes
brainrender.settings.SHADER_STYLE = "plastic"  # affects the look of rendered brain regions: [cartoon, metallic, plastic, shiny, glossy]
brainrender.settings.DEFAULT_ATLAS = "allen_mouse_25um" 
brainrender.settings.DEFAULT_CAMERA = "three_quarters"
    #[sagittal, sagittal2, frontal, top, top_side, three_quarters]
brainrender.settings.SCREENSHOT_SCALE = 1
brainrender.settings.ROOT_ALPHA = 0.2  # transparency of the overall brain model's actor'

#Define brain regions - leave arrays empty if plotting all cells
#Use region ID (regions) and/or acronyms to isolate cells
regions = [767]
acronyms = ["MOs5"]

#MOs = 993
#SS = 453
#MOp = 985



def read_in_BrainJ_cells(filename, regions, acronyms):
    #this function reads in BrainJ csv files and can be used to filter to region at the same time
    #use pandas to read in specific columns from BrainJ csv output file
    cells = pd.read_csv(filename, usecols=[0,1,3,12,13], names = ['X','Y','Z','ID','Ac'], #, usecols=col_list)
                          skiprows = [0]) #skip header row
    
    #Filter based on regions array 
    if len(regions) > 0:
      cells = cells[cells['ID'].isin(regions)]
    #print(cells)
    
    #Filter cells in specific region using acronyms array
    if len(acronyms) > 0:
      cells = cells[cells['Ac'].isin(acronyms)]
    #print(cells)
    
   
    #create lists from cells table - note swapping X and Y axes to match brainrender orientation
    Z = cells['X'].tolist()
    Y = cells['Y'].tolist()
    X = cells['Z'].tolist()
    
    
    #data is in voxels, so multiply by atlas resolution (25micronXYZ)
    AtlasRes = 25
    X = [element * AtlasRes for element in X]
    Y = [element * AtlasRes for element in Y]
    Z = [element * AtlasRes for element in Z]
    pts = [[x, y, z] for x, y, z in zip(X, Y, Z)]
    return np.vstack(pts)

#use function to read in and filter cells
coordinates1 = read_in_BrainJ_cells(cellsfile, regions, acronyms)
#coordinates2 = read_in_BrainJ_cells(cellsfile2, regions, acronyms)

#create the scene and give a title if required
scene = Scene(title="Cells from BrainJ")
# Setting a screenshot save directory
#scene = Scene(title="Cells", screenshots_folder="C:\\Users\\Luke_H\\Documents\\GitHub") 
#inset=True (False turns off brain outline)

#add in the relevant brain regions - use acronyms as below
scene.add_brain_region("MOs", alpha=0.35)
scene.add_brain_region("SS", alpha=0.35)
scene.add_brain_region("MOp", alpha=0.35)

# Add to points to scene and give colour
scene.add(Points(coordinates1, name="Cells", colors="steelblue"))
#scene.add(Points(coordinates2, name="Cells", colors="salmon"))

# uncomment to add density to plot to scene
#scene.add(PointsDensity(coordinates1))

# render
scene.content
scene.render()
