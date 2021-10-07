#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap Script - Cellular Imaging / Zuckerman Institute
=======

This script has been modified from the provided ClearMap2.0 script.

This script is the main pipeline to analyze immediate early gene expression 
data from iDISCO+ cleared tissue [Renier2016]_.

See the :ref:`CellMap tutorial </CellMap.ipynb>` for a tutorial and usage.


.. image:: ../Static/cell_abstract_2016.jpg
   :target: https://doi.org/10.1016/j.cell.2020.01.028
   :width: 300

.. figure:: ../Static/CellMap_pipeline.png

  iDISCO+ and ClearMap: A Pipeline for Cell Detection, Registration, and 
  Mapping in Intact Samples Using Light Sheet Microscopy.


References
----------
.. [Renier2016] `Mapping of brain activity by automated volume analysis of immediate early genes. Renier* N, Adams* EL, Kirst* C, Wu* Z, et al. Cell. 2016 165(7):1789-802 <https://doi.org/10.1016/j.cell.2016.05.007>`_
"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

if __name__ == "__main__":
     
  #%%############################################################################
  ### Initialization 
  ###############################################################################
  
  
  #%% Initialize workspace

  #import numpy as np



  #%% Initialize workspace

  #ClearMap path
  import sys
  sys.path.append('/home/luke/Documents/Github/ClearMap2')
    
  from ClearMap.Environment import *  #analysis:ignore
  

  
  #directories and files
  directory = '/home/luke/Desktop/haloperidol/1268'    
  
  #expression_raw      = 'cfos/17-14-34_0_8X-cfos_UltraII_C00_xyz-Table Z<Z,4>.ome.tif'           
 # expression_auto     = 'autof/18-15-14_0_8X-autofluo_UltraII_C00_xyz-Table Z<Z,4>.ome.tif'  
  expression_raw      = 'cfos/14-22-33_0_8X-cfos_UltraII_C00_xyz-Table Z<Z,4>.ome.tif'           
  expression_auto     = 'autof/15-30-26_0_8X-autofluo_UltraII_C00_xyz-Table Z<Z,4>.ome.tif'   
  
  ws = wsp.Workspace('CellMap', directory=directory);
  ws.update(raw=expression_raw, autofluorescence=expression_auto)
  ws.info()
  
  ws.debug = False
  
  resources_directory = settings.resources_path
  
  #%% Display troubleshooting
  #import pyqtgraph as pg
  #import vispy
  vispy.use('PyQt5')
  print(pg.QtCore.PYQT_VERSION_STR)
  
  #%% Initialize alignment 
  
  #init atals and reference files
  
  #NOTE: any changes to orientation here will affect the output orientation (e.g. cell location coordinates etc)
  # When plotting data later, or combining datasets, ensure all data is the same orientation
  annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
      slicing=(slice(None),slice(None),slice(0,228)), orientation=(1,2,3), #Hemisphere
      #slicing=(slice(None),slice(None),slice(None)), orientation=(1,2,3), #Whole Brain
      overwrite=False, verbose=True);
  
  #alignment parameter files    
  align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
  align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
  align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')
  
  
  #%%############################################################################
  ### Data conversion
  ############################################################################### 
  
  #%% Convet raw data to npy file     
               
  source = ws.source('raw');
  sink   = ws.filename('stitched')
  io.delete_file(sink)
  io.convert(source, sink, processes=None, verbose=True);
  
  # write header to view in imageJ
  io.mhd.write_header_from_source(ws.filename('stitched'), filename=None, header=None)
  
  
  #%%############################################################################
  ### Resampling and atlas alignment 
  ###############################################################################
        
  #%% Resample 
             
  resample_parameter = {
      "source_resolution" : (4.0625, 4.0625, 3),
      "sink_resolution"   : (25,25,25),
      "processes" : 4,
      "verbose" : True,             
      };
  
  io.delete_file(ws.filename('resampled'))
  
  res.resample(ws.filename('stitched'), sink=ws.filename('resampled'), **resample_parameter)
  
  #%%
  #p3d.plot(ws.filename('resampled'))
  
  #%% Resample autofluorescence
      
  resample_parameter_auto = {
      "source_resolution" : (4.0625, 4.0625, 3), #resolution of original clearmap data
      "sink_resolution"   : (25,25,25),
      "processes" : 4,
      "verbose" : True,                
      };    
  
  res.resample(ws.filename('autofluorescence'), sink=ws.filename('resampled', postfix='autofluorescence'), **resample_parameter_auto)
  
  #p3d.plot([ws.filename('resampled'), ws.filename('resampled', postfix='autofluorescence')])
  
  #%% Aignment - resampled to autofluorescence (>2min - update elastix?)
  
  # align the two channels
  align_channels_parameter = {            
      #moving and reference images
      "moving_image" : ws.filename('resampled', postfix='autofluorescence'),
      "fixed_image"  : ws.filename('resampled'),
      
      #elastix parameter files for alignment
      "affine_parameter_file"  : align_channels_affine_file,
      "bspline_parameter_file" : None,
      
      #directory of the alig'/home/nicolas.renier/Documents/ClearMap_Ressources/Par0000affine.txt',nment result
      "result_directory" :  ws.filename('resampled_to_auto')
      }; 
  
  elx.align(**align_channels_parameter);
  
  #%% Alignment - autoflourescence to reference - 7-9min (improve with new version of elastix?)
  
  # align autofluorescence to reference
  align_reference_parameter = {            
      #moving and reference images
      "moving_image" : reference_file,
      "fixed_image"  : ws.filename('resampled', postfix='autofluorescence'),
      
      #elastix parameter files for alignment
      "affine_parameter_file"  :  align_reference_affine_file,
      "bspline_parameter_file" :  align_reference_bspline_file,
      #directory of the alignment result
      "result_directory" :  ws.filename('auto_to_reference')
      };
  
  elx.align(**align_reference_parameter);
  
  
  #%%############################################################################
  ### Create test data
  ###############################################################################
  
  #%% Crop test data 
  
  #select sublice for testing the pipeline
  
  slicing = (slice(30,700),slice(900,1500),slice(1340,1850));
  ws.create_debug('stitched', slicing=slicing);
  ws.debug = True; #or ws.debug = 'name_for_the_test_subset'
  
  #p3d.plot(ws.filename('stitched'))
  
  #%%############################################################################
  ### Cell detection
  ###############################################################################
  
  #%% Cell detection:  Aprox 7min
  
  cell_detection_parameter = cells.default_cell_detection_parameter.copy();
  cell_detection_parameter['iullumination_correction']['flatfield'] = None;
  #cell_detection_parameter['background'] = None;
  cell_detection_parameter['background_correction']['shape'] = (7,7);
  cell_detection_parameter['background_correction']['form'] = 'Disk';
  #cell_detection_parameter['background_correction']['save'] = ws.filename('cells', postfix='bgremove');
  cell_detection_parameter['intensity_detection']['measure'] = ['source'];
  cell_detection_parameter['shape_detection']['threshold'] = 1200;
  
  io.delete_file(ws.filename('cells', postfix='maxima')) # deletes existing cells maxima file
  cell_detection_parameter['maxima_detection']['shape'] = 3 #5 #size of structural element - should be near typical size of cell
  cell_detection_parameter['maxima_detection']['threshold'] = 700 #only maxima above this intensity are detected
  #cell_detection_parameter['maxima_detection']['save'] = ws.filename('cells', postfix='maxima')
 
  #Parameters for block processing   for 128GB RAM  6, 100,50,16, chunkoptTrue, chunkoptsizeall, processparaellel
  processing_parameter = cells.default_cell_detection_processing_parameter.copy();
  processing_parameter.update(
      processes = 6, # 32, 6, 'serial',
      size_max = 100, #100, #35, 20 35     
      size_min = 50,# 30, #30, 11  25
      overlap  = 16, #32, #10, 10  10
      verbose = True
      )
  
  cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                     cell_detection_parameter=cell_detection_parameter, 
                     processing_parameter=processing_parameter)
  
  # add in tif conversion or header for imagej viewing of cell detection results
  #io.mhd.write_header_from_source(ws.filename('cells_filtered'), filename=None, header=None)
  
  
  #%% visualization
  #p3d.plot(ws.filename('cells', postfix='bgremove'))
  
  p3d.plot([[ws.filename('stitched'), ws.filename('cells', postfix='maxima')]])
  
  #%%
  coordinates = np.hstack([ws.source('cells', postfix='raw')[c][:,None] for c in 'xyz']);
  p = p3d.list_plot_3d(coordinates)
  
  #p3d.plot_3d(ws.filename('stitched'), view=p, cmap=p3d.grays_alpha(alpha=1))
  
  
  #%% Cell statistics
  
  source = ws.source('cells', postfix='raw')
  
  plt.figure(1); plt.clf();
  names = source.dtype.names;
  nx,ny = p3d.subplot_tiling(len(names));
  for i, name in enumerate(names):
    plt.subplot(nx, ny, i+1)
    plt.hist(source[name]);
    plt.title(name)
  plt.tight_layout();
  
  #%% Filter cells and plot filtered cell statistics
  
  thresholds = { # can filter on any column in the cells table
      'source' : None, #this could be measured intensity ?
      'size'   : (20,900) #filter cells based on size range
      }
  
  cells.filter_cells(source = ws.filename('cells', postfix='raw'), 
                     sink = ws.filename('cells', postfix='filtered'), 
                     thresholds=thresholds);
  
  
  source = ws.source('cells', postfix='filtered')
  
  plt.figure(1); plt.clf();
  names = source.dtype.names;
  nx,ny = p3d.subplot_tiling(len(names));
  for i, name in enumerate(names):
    plt.subplot(nx, ny, i+1)
    plt.hist(source[name]);
    plt.title(name)
  plt.tight_layout();
  
  
  
  #%% Visualize
  
  coordinates = np.array([ws.source('cells', postfix='filtered')[c] for c in 'xyz']).T;
  p = p3d.list_plot_3d(coordinates, color=(1,0,0,0.5), size=10)
  #p3d.plot_3d(ws.filename('stitched'), view=p, cmap=p3d.grays_alpha(alpha=1))
  #p3d.plot([[ws.filename('stitched'), ws.filename('cells', postfix='filtered')]]) #list of points
  
  
  #%%############################################################################
  ### Cell atlas alignment and annotation
  ###############################################################################
  
  #%% Cell alignment
  
  source = ws.source('cells', postfix='filtered')
  
  def transformation(coordinates):
    coordinates = res.resample_points(
                    coordinates, sink=None, orientation=None, 
                    source_shape=io.shape(ws.filename('stitched')), 
                    sink_shape=io.shape(ws.filename('resampled')));
    
    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=ws.filename('resampled_to_auto'), 
                    binary=True, indices=False);
    
    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=ws.filename('auto_to_reference'),
                    binary=True, indices=False);
        
    return coordinates;
    
  
  coordinates = np.array([source[c] for c in 'xyz']).T;
  
  coordinates_transformed = transformation(coordinates);
  
 #%% Cell annotation
  # *** by default this script only provides graph order - which may confuse some users after region ID
  # updated to include ID and acronyms
  # in tutorial show people the json file to understand regions
  
  label = ano.label_points(coordinates_transformed, key='order');
  names = ano.convert_label(label, key='order', value='name');
  ID = ano.convert_label(label, key='order', value='id');
  acronym = ano.convert_label(label, key='order', value='acronym');
  
  #%% Save results
  #adding in ID and acronyms as above
  #IMPORTANT - names should be final column, as comma seperated names create additional columns and 
  #will mix entries in columns to the right of the names column
  # keep in mind, first letter of column name used in output - so "atlas_ID" and "acronym" would be both be save to column "a"
  
  coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
  label = np.array(label, dtype=[('order', int)]);
  names = np.array(names, dtype=[('name' , 'U256')])
  ID = np.array(ID, dtype=[('id' , int)])
  acronym = np.array(acronym, dtype=[('acronym' , 'U256')])
  
  import numpy.lib.recfunctions as rfn
  cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, ID, acronym, names], flatten=True, usemask=False)
  
  io.write(ws.filename('cells'), cells_data)
    
  
  
  #%%############################################################################
  ### Cell csv generation for external analysis
  ###############################################################################
  
  #%% CSV export
  
  source = ws.source('cells');
  header = ', '.join([h[0] for h in source.dtype.names]);
  np.savetxt(ws.filename('cells', extension='csv'), source[:], header=header, delimiter=',', fmt='%s')
  
  #%% ClearMap 1.0 export
  
  source = ws.source('cells');
  
  clearmap1_format = {'points' : ['x', 'y', 'z'], 
                      'points_transformed' : ['xt', 'yt', 'zt'],
                      'intensities' : ['source', 'dog', 'background', 'size']}
  
  for filename, names in clearmap1_format.items():
    sink = ws.filename('cells', postfix=['ClearMap1', filename]);
    data = np.array([source[name] if name in source.dtype.names else np.full(source.shape[0], np.nan) for name in names]);
    io.write(sink, data);
  
  
  #%%############################################################################
  ### Voxelization - cell density
  ###############################################################################
  
  source = ws.source('cells')
  
  coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
  intensities = source['source'];
  
  #%% Unweighted 
  
  voxelization_parameter = dict(
        shape = io.shape(annotation_file), 
        dtype = None, 
        weights = None,
        method = 'sphere', 
        radius = (7,7,7), 
        kernel = None, 
        processes = None, 
        verbose = True
      )
  
  vox.voxelize(coordinates, sink=ws.filename('density', postfix='counts'), **voxelization_parameter);
  
  
  #%% 
  
  #p3d.plot(ws.filename('density', postfix='counts'))
  
  
  #%% Weighted 
  
  voxelization_parameter = dict(
        shape = io.shape(annotation_file),
        dtype = None, 
        weights = intensities,
        method = 'sphere', 
        radius = (7,7,7), 
        kernel = None, 
        processes = None, 
        verbose = True
      )
  
  vox.voxelize(coordinates, sink=ws.filename('density', postfix='intensities'), **voxelization_parameter);
  
  #%%
  
  #p3d.plot(ws.filename('density', postfix='intensities'))
