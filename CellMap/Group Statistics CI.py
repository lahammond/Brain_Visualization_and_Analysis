#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 16:18:33 2021

@author: Luke Hammond

Statistics script for ClearMap2

"""
     
  #%%############################################################################
  ### Initialization 
  ###############################################################################
  
  import numpy as np
  
  #ClearMap path
  import sys
  sys.path.append('/home/luke/Documents/Github/ClearMap2')
  
  #Set output directory for saving files
  output_dir = '/home/luke/Desktop/haloperidol' 
  
  
  #import ClearMap
  from ClearMap.Environment import *  #analysis:ignore
  import ClearMap.Analysis.Statistics.GroupStatistics as stat
  
  #%% Load heat map images - here we are using the example datasets from ClearMap1
  
  
  group1 = ['/home/luke/Desktop/haloperidol/1267/density_counts.tif',
            '/home/luke/Desktop/haloperidol/1268/density_counts.tif',
            '/home/luke/Desktop/haloperidol/1269/density_counts.tif'
          ];
  group2 = ['/home/luke/Desktop/Saline/1272/density_counts.tif',
           '/home/luke/Desktop/Saline/1273/density_counts.tif',
           '/home/luke/Desktop/Saline/1274/density_counts.tif'
           ];

  g1 = stat.read_group(group1) # read_group included in t_test_vox function
  g2 = stat.read_group(group2)

  #%% Create average and standard deviation heatmaps for each group
  g1m = np.mean(g1,axis = 0)
  io.tif.write(os.path.join(output_dir,'group1_mean.tif'), g1m)
 
  g1s = np.std(g1,axis = 0);
  io.tif.write(os.path.join(output_dir,'group1_std.tif'), g1s)

  g2m = np.mean(g2,axis = 0)
  io.tif.write(os.path.join(output_dir,'group2_mean.tif'), g2m)
 
  g2s = np.std(g2,axis = 0);
  io.tif.write(os.path.join(output_dir,'group2_std.tif'), g2s)

  #%% Generate p values
  pvals, psign = stat.t_test_voxelization(group1, group2, signed=True, remove_nan=True, p_cutoff=0.05)
  pvalscolor = stat.color_p_values(pvals, psign, positive = [0,1], negative = [1,0])
  io.tif.write(os.path.join(output_dir,'pvalues.tif'), pvalscolor.astype('float32'))
  #need to update to change shape.
  #io.tif.write(os.path.join(output_dir,'pvalues.tif'), pvalscolor[:,:,:,1].astype('float32'))