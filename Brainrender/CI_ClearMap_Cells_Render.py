# brainrender script for plotting cells from ClearMap 

# Author: 	Luke Hammond
# Cellular Imaging | Zuckerman Institute, Columbia University
# Date:	1st October, 2021

import numpy as np

import brainrender
from brainrender import Scene
from brainrender.actors import Points, PointsDensity
from brainrender.actors import Volume

from rich import print
from myterial import orange
from pathlib import Path
import pandas as pd

#if making videos
from brainrender import VideoMaker

#Modify Settings
brainrender.settings.WHOLE_SCREEN = False  # make the rendering window be smaller
brainrender.settings.SHOW_AXES = False
brainrender.settings.SHADER_STYLE = "plastic"  #[cartoon, metallic, plastic, shiny, glossy]
brainrender.settings.DEFAULT_ATLAS = "allen_mouse_25um" 
brainrender.settings.DEFAULT_CAMERA = "three_quarters"
    #[sagittal, sagittal2, frontal, top, top_side, three_quarters]
brainrender.settings.SCREENSHOT_SCALE = 1
brainrender.settings.ROOT_ALPHA = 0.2  # transparency of the overall brain model's actor'


print(f"[{orange}]Running example: {Path(__file__).name}")


# Provide path to ClearMap cells csv file that you wish to plot
cellsfile1 = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/ClearMap/CellMap_Sa_cfos.csv"
cellsfile2 = "C:/Users/Luke_H/Desktop/3_Brain_Visualization_Workshop/ClearMap/CellMap_Ha_cfos.csv"

#Define brain regions - leave array empty if plotting all cells
#CP = 672 SNr = GPe = GPi = PF = 930 PPN = STN = STR =477
regions = [672]
acronyms = ["CP"]

def read_in_ClearMap_cells(filename, regions, acronyms):
    #this function reads in ClearMap csv files and can be used to filter to region at the same time
    #expects csv created using modified cellmap protocol, with region IDs and acronyms included
    #use pandas to read in specific columns from BrainJ csv output file
    cells = pd.read_csv(filename, usecols=[5,6,7,9,10], names = ['X','Y','Z','ID','Ac'], #, usecols=col_list)
                          skiprows = [0]) #skip header row

    #Filter cells out side of the brain
    cells = cells[cells['ID'] != 0]
    
    #Filter cells in specific regions - by ID
    if len(regions) > 0:
      cells = cells[cells['ID'].isin(regions)]
    
    #Filter cells in specific region - by abbreviation
    if len(acronyms) > 0:
      cells = cells[cells['Ac'].isin(acronyms)]
    #print(cells)

    Y = cells['X'].tolist()
    X = cells['Y'].tolist()
    Z = cells['Z'].tolist()
    #ID = cells['ID'].tolist()

    #If orientation was flipped during processing in ClearMap (e.g. slicing 
    # orientation=(1,-2,3) vs orientation=(1,2,3)) then reverse the order of that axis such as:
    #X = X[::-1]
    
    #data is in voxels, so multiply by atlas resolution (25micronXYZ)
    AtlasRes = 25
    X = [element * AtlasRes for element in X]
    Y = [element * AtlasRes for element in Y]
    Z = [element * AtlasRes for element in Z]
    pts = [[x, y, z] for x, y, z in zip(X, Y, Z)]
    return np.vstack(pts)


# use clearmap importer function to read in cell coordinates
coordinates1 = read_in_ClearMap_cells(cellsfile1, regions, acronyms)
coordinates2 = read_in_ClearMap_cells(cellsfile2, regions, acronyms)

#Create the scene

scene = Scene(title="Cells from ClearMap")

# Setting a screenshot save directory
#scene = Scene(title="Cells", screenshots_folder="C:\\Users\\Luke_H\\Documents\\GitHub") 
    #inset=True (False turns off brain outline)


#Add in brain regions
scene.add_brain_region("CP", alpha=0.35)
scene.add_brain_region("STR", alpha=0.35)


# Add points to scence

scene.add(Points(coordinates1, name="CELLS", colors="magenta", alpha=0.2))
scene.add(Points(coordinates2, name="CELLS", colors="springgreen", alpha=0.2))


#Add density to scene - using modified method to allow different colors for densities

Density1 = Volume(PointsDensity(coordinates1, radius=500).color('Purples'),
                  voxel_size=25,
                  as_surface=False,
                  )


Density2 = Volume(PointsDensity(coordinates2, radius=500).color('Greens'),
                  voxel_size=25,
                  as_surface=False,
                  )


# add in density volume actors

scene.add(Density1)
scene.add(Density2)

# Cut with plane if only hemisphere - uncomment to slice to one hemisphere
#scene.slice("sagittal")

# render the scene

scene.content
#modify zoom using argument in render below
scene.render(zoom=0.8)



#Alternatively - Render as rotating video
# Create an instance of video maker
vm = VideoMaker(scene, "./Movies", "Movie1")
# Create video
# azimuth = X #elevation = Y #roll= X
# e.g. 1 = 1 degree per frame
vm.make_video(duration=3, azimuth=5, fps=15)

#Alternatively - render with key frames
#anim = Animation(scene, "./examples", "vid3")

#anim.add_keyframe(0, camera="top", zoom=1.3)
#anim.add_keyframe(1, camera="sagittal", zoom=3)
#anim.add_keyframe(2, camera="frontal", zoom=0.8)
#anim.add_keyframe(3, camera="frontal", )

#anim.make_video( duration=3, fps=15)
