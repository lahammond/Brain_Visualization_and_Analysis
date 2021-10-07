# brainrender script for plotting cells and volumes from BrainJ 

# Author: 	Luke Hammond
# Cellular Imaging | Zuckerman Institute, Columbia University
# Date:	1st October, 2021

import numpy as np

import brainrender
from brainrender import Scene
from brainrender.actors import Points

#for volumes
from imio import load
from brainrender.actors import Volume

#for plotting cylinder and ruler
from brainrender.actors import Cylinder
from brainrender.actors import ruler, ruler_from_surface

from rich import print
from myterial import orange
from pathlib import Path
import pandas as pd

print(f"[{orange}]Running example: {Path(__file__).name}")

#Path to csv file containing cell locations - can load multiple cell files and plot together
cellsfile = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/BrainJ/C1_Detected_Cells.csv"
cellsfile2 = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/BrainJ/C2_Detected_Cells.csv"

#Path to .tif file containg images transformed to CCF
volfile = "C:\\Users\\Luke_H\\Desktop\\3_Brain_Visualization_Workshop\\BrainJ\\C1_raw_data_in_atlas_space.tif"


#Modify Settings
brainrender.settings.WHOLE_SCREEN = False  # make the rendering window smaller - full screen required for animations
brainrender.settings.SHOW_AXES = False #show/hide axes
brainrender.settings.SHADER_STYLE = "plastic"  # affects the look of rendered brain regions: [cartoon, metallic, plastic, shiny, glossy]
brainrender.settings.DEFAULT_ATLAS = "allen_mouse_25um" 
brainrender.settings.DEFAULT_CAMERA = "three_quarters"
    #[sagittal, sagittal2, frontal, top, top_side, three_quarters]
brainrender.settings.SCREENSHOT_SCALE = 1
brainrender.settings.ROOT_ALPHA = 0.2  # transparency of the overall brain model's actor'

#arrays for filtering cells to specific regions - leave empty to plot all
regions = []
acronyms = []

#regions = [767]
#acronyms = ["MOs5"]


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
scene.add_brain_region("CP", alpha=0.35)

# Add to points to scene and give colour
scene.add(Points(coordinates1, name="Cells", colors="steelblue"))
#scene.add(Points(coordinates2, name="Cells", colors="salmon"))

# Add image data
vol = load.load_any(volfile)
#print(vol.shape)
#Swap axes as BrainJ data is coronal
vol = np.swapaxes(vol, 0,2)

# make a volume actor - adjust color and turn/off meshing 
Vol_actor = Volume(
    vol,
    voxel_size=25,  # size of a voxel's edge in microns
    as_surface=False,  # if true a surface mesh is rendered instead of a volume
    min_value=100, 
    cmap="Greens", # color for surface
    c="Reds",  # use matplotlib colormaps to color the volume
)
#add the volume 
scene.add(Vol_actor)


# adding a cylinder as a GRIN lens
# locate the XYZ coordinate of the grin lens in the brain-use a data set transformed to the CCF space from BrainJ
# Note Z = X and X = Z
#position =  [337,144,173] so 
position =  [173,144,337]

#multiply by atlas resolution to plot correctly
AtlasRes = 25
position = [element * AtlasRes for element in position]
# create and add a cylinder actor
Cylinder_actor = Cylinder( 
    position,  # center the cylinder at the center of mass of th
    scene.root,  # the cylinder actor needs information about the root mesh
)
#add the cylinder
scene.add(Cylinder_actor)


#measuring the distance of the GRIN lens insertion from the surface of the brain
#won't be visible if rendered with cyclinder so only render one at a time
# will use the same position information as we used when plotting the cylinder
Ruler_actor = ruler_from_surface(position, scene.root, unit_scale=0.01, units="mm")
scene.add(Ruler_actor)


# render the scene
scene.content
scene.render()
