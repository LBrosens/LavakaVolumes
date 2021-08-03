# LavakaVolumes
Dataset and PyQGIS code for the automated determination of lavaka (gully) volumes in QGIS based on three different DEM sources: TanDEM-X, SRTM and a high-resolution UAV-SfM DEM. Lavaka volumes were determined for 699 lavaka in 6 study areas in the lake Alaotra region (Madagascar) and builds upon this earlier published dataset (https://doi.org/10.6084/m9.figshare.c.5236322.v1).

Individual lavaka volumes were determined from the difference between the current surface and a reconstructed pre-erosionsurface. This was done by developing an automated workflow in PyQGIS written in QGIS version 3.8.1 with GRASS 7.6.1. The automated PyQGIS workflow consists of 6 steps which are explained in detail below. The input data required to run the procedure is discussed in step 0. 

In This repository three main files can be found:
  1) the PyGis code to obtain the volumes in QGIS
  2) An example dataset containing input and output files for a test area: three lavaka and SRTM DEM
  3) An excel table containing the results of the full lavaka dataset organized in different sheets:
      - Original volumes UAV-SfM:the presented volumes are ontained as the difference between the interpolated (spline interpolation) pre-erosion surface and the current               surface for the UAV-SfM DEM
      - Original volumes TanDEM-X: the presented volumes are ontained as the difference between the interpolated (spline interpolation) pre-erosion surface and the current             surface for the TanDEM-X DEM
      - Original volumes SRTM: the presented volumes are ontained as the difference between the interpolated (spline interpolation) pre-erosion surface and the current surface         for the SRTM DEM
      - applied A-V TanDEM-X:the presented volumes are obtained after applying the breakpoint area-volume relationship based on the TanDEM-X spline volumes to the lavaka areas         of 1949, 1969 and 2010s
      - applied A-V UAV-SfM: the presented volumes are obtained after applying the area-volume relationship based on the UAV-SfM spline volumes to the lavaka areas of 1949,             1969 and 2010s

# Workflow Volume determination PyGIS code 

STEP 0: Input data
Three  input  files  are  required  to  run  the  automated  volume-procedure:  
i)  a  shapefile  containing  the  digitized  lavakaoutlines, 
ii) a shapefile containing a pre-erosion surface polygon for each lavaka and 
iii) a DEM raster file. 
A manual delineation-procedure was followed to obtain the pre-erosion surface where a horseshoe-shaped polygon was drawn around each individual lavaka on the hillslope parts that were unaffected by erosion 

STEP 1: Create points in pre-erosion polygon
Random points are created in the pre-erosion surface polygons. The number of points (N) is made dependent on the area(A, m2): N = A/20, with a minimum distance of 1 m (Fig. 2a).140

STEP 2: Assign DEM-values to points
Each point is assigned the elevation value from the corresponding DEM-pixel.

STEP 3: Interpolate pre-erosion surface
The pre-erosion surface is obtained by interpolating between the pre-erosion polygon points. Two interpolation methodswere used: i) Triangulated Irregular Network (TIN) and ii) spline interpolation. 

STEP 4: Calculate elevation difference
The current DEM is subtracted from the interpolated pre-erosion surface. The result is a difference raster with positivevalues indicating a current surface that is lower than the reconstructed pre-erosion surface. Negative values indicate thatthe current topography is higher than the reconstructed topography, which is physically impossible.

STEP 5: Elevation difference clipped to lavaka extent
The lavaka extent, which is given by the digitized lavaka polygon, is clipped from the elevation difference raster. In this way a raster with the elevation difference over the lavaka area is obtained. If the lavaka is smaller than onepixel (0.04 m2, 144 m2and 900 m2for the UAV-SfM, TanDEM-X and SRTM DEM, respectively) the resulting raster is empty and no volume can be calculated.

STEP 6: Export results
The unique values report of the lavaka elevation difference raster is exported. It contains the unique elevation values,160their count and dimensions of the raster pixels. These results are used to calculate the volumes of each lavaka.


