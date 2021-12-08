# LavakaVolumes
Dataset and PyQGIS code for the automated determination of lavaka (gully) volumes in QGIS based on three different DEM sources: 12 m TanDEM-X, 30 m Copernicus and a 0.20 m resolution UAV-SfM DEM. Lavaka volumes were determined for 699 lavaka in 6 study areas in the lake Alaotra region (Madagascar) and builds upon this earlier published dataset (https://doi.org/10.6084/m9.figshare.c.5236322.v1). This workflow and the results are discussed in detail here: https://doi.org/10.5194/esurf-2021-64

Individual lavaka volumes were determined from the difference between the current surface and a reconstructed pre-erosionsurface. This was done by developing an automated workflow in PyQGIS written in QGIS version 3.16.10. The automated PyQGIS workflow consists of 6 steps which are explained in detail below. The input data required to run the procedure is discussed in step 0. 

In This repository three main files can be found:
  1) the PyGis code to obtain the volumes in QGIS
  2) An example dataset containing input and output files for a test area: three lavaka and Copernicus DEM
  3) An excel table containing the results of the full lavaka dataset organized in different sheets:
      - Volumes UAV-SfM: volumes obtained as the difference between the interpolated (regularized spline with tension interpolation) pre-erosion surface and the    current surface for the 0.20 m resolution UAV-SfM DEM.
      - Volumes TanDEM-X: volumes obtained as the difference between the interpolated (regularized spline with tension interpolation) pre-erosion surface and the current surface for the 12 m resolution TanDEM-X DEM
      - Volumes Copernicus: volumes obtained as the difference between the interpolated (regularized spline with tension interpolation) pre-erosion surface and the current surface for the 30 m resolution SRTM DEM.
       - applied A-V UAV-SfM: the presented volumes are obtained after applying the area-volume relationship based on the UAV-SfM spline volumes to the lavaka areas of 1949, 1969 and 2010s
       - applied A-V TanDEM-X: the presented volumes are obtained after applying the breakpoint area-volume relationship based on the TanDEM-X volumes to the lavaka areas of 1949, 1969 and 2010s
       - applied A-V Copernicus: the presented volumes are obtained after applying the breakpoint area-volume relationship based on the Copernicus volumes to the lavaka areas of 1949, 1969 and 2010s

Two types of uncertainties are taken into account when calculating the volumes: the interpolation error and the relative height error. These uncertainties are incorporated by running a Monte Carlo analysis (10 000 runs), where the mean and standard deviation are reported for the calculated volumes in the first three excel sheets. For the volumes calculated by applying the area-volume relationship to the lavaka areas of 1949, 1969 and 2010s the uncertainties on the fitted regression coefficients are taken into account by again running a Monte Carlo analysis. The mean and std of the obtained volumes and volumetric growth rates are reported in the last three excel sheets. 

# Workflow Volume determination PyGIS code 
The PyGis code should be run in the python console of QGis version 3.16.10. (https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/intro.html?highlight=python%20console#scripting-in-the-python-console).
The script can be opened in the Python console. Folder paths should be changed to the user's folder structure and the needed subfolder need to be created in order to properly save the created files. More detailed instructions are given in the LavakaVolumesPyQGIS_v2.py script itself. 

STEP 0: Input data
Three  input  files  are  required  to  run  the  automated  volume-procedure:  
i)  a  shapefile  containing  the  digitized  lavaka outlines, 
ii) a shapefile containing a pre-erosion surface polygon for each lavaka and 
iii) a DEM raster file. 
A manual delineation-procedure was followed to obtain the pre-erosion surface where a horseshoe-shaped polygon was drawn around each individual lavaka on the hillslope parts that were unaffected by erosion. The id's of the lavaka need to match the id's of the pre-erosion polygons.

STEP 1: Clip the DEM to the extent of the pre-erosion polygon
The DEM file is clipped to with the pre-erosion polygon in order to extract the pixels that contain the pre-erosion elevations. 

STEP 2: Create one point per pixel
On point per pixel is created for the clipped pre-erosion DEM file. The height of the pixel is assigned to the point.

STEP 3: Interpolate the pre-erosion surface
The pre-erosion surface is obtained by interpolating between the pre-erosion polygon points. Five interpolation methods were used: i) Linear interpolation (GDAL), ii) TIN interpolation (QGIS), Regularized spline with tension (GRASS GIS), iv) Bilinear spline (GRASS GIS) and v) Bicubic spline interpolation (GRASS GIS).

STEP 4: Calculate elevation difference
The current DEM is subtracted from the interpolated pre-erosion surface. The result is a difference raster with positive values indicating a current surface that is lower than the reconstructed pre-erosion surface. Negative values indicate thatthe current topography is higher than the reconstructed topography, which is physically impossible.

STEP 5: Elevation difference clipped to lavaka extent
The lavaka extent, which is given by the digitized lavaka polygon, is clipped from the elevation difference raster. In this way a raster with the elevation difference over the lavaka area is obtained. If the lavaka is smaller than onepixel (0.04 m², 144 m² and 900 m² for the UAV-SfM, TanDEM-X and Copernicus DEM, respectively) the resulting raster is empty and no volume can be calculated.

STEP 6: Export results
The unique values report of the lavaka elevation difference raster is exported. It contains the unique elevation values, their count and dimensions of the raster pixels. These results are used to calculate the volumes of each lavaka.

These exported unique value files can then be further processed and analyzed. 
