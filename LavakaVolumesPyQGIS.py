#################################################################################
#-------------------------------------------------------------------------------#
#							LAVAKA VOLUME DETERMINATION
#-------------------------------------------------------------------------------#
#################################################################################

# This PyQGIS script is written by L. Brosens in QGIS version 3.8.1 with GRASS 
# 7.6.1. This script is used to reconstruct the original topography around a 
# lavaka and to calculate the lavaka volume as the difference between the 
# reconstructed topography and current topography.

# The input files and different steps to obtain the volumes are described below. 
# Folder directions and file names will have to be adapted to the user's names

# last changes made: 02/8/2021
# contact: liesa.brosens@kuleuven.be

#################################################################################
#                   STEP 0: READ IN THE SHAPEFILES
#################################################################################
# as a first step the necessary folder directions are set and the three required
# input files are loaded
    # 1) shapefile containing the digitized lavaka outlines: 'Lavaka.shp'
    # 2) shapefile containing a pre-erosion surface polygon for each lavaka: 'Poly_OriSurf.shp' 
    # 3) DEM raster file: 'DEM.tif'
# All files are in UTM coordinates. The ID of the pre-erosion polygons must 
# corrspond with the id (first part of the name) of the lavaka polygon.

# Set the folder in which all files are stored and make this the working directory
path = 'C:/Folder/subfolder/.../Lavaka_Volumes/example/'
os.chdir(path)

# Read in the files
DEM = path+'SRTM.tif'
poly_surf = path+'poly_OriginalSurf.shp'
lavaka = path+'lavaka.shp'
    
# load the shapefile layers
lavaka_layer = QgsVectorLayer(lavaka, 'lavaka', 'ogr')
poly_layer = QgsVectorLayer(poly_surf, 'poly', 'ogr')

# Set the interpolation method (Spline = 1 or TIN = 2)
interpol_method = 2

################################################################################
#                   TOO CHECK BEFORE CONTINUING
################################################################################
# Some final checks before starting the analysis:
    # 1. check if the shafile layers are correctly loaded 
if not lavaka_layer.isValid():
    print("Lavaka layer failed to load!")

if not poly_layer.isValid() :
    print("Poly layer failed to load!")
    
    # 2. check if the x and y resolution of the DEM are EXACTLY the same.
    # (Properties -> Information -> Pixel Size)
    # If not: warp (reproject) -> define the resolution and save the DEM 

    # 3. check if the lavaka polygon layer has a field 'id'.
    # If not: create id field and fill it with the id's by using the code below
    # Create field 'id':
from PyQt5.QtCore import QVariant
layer_provider=lavaka_layer.dataProvider()
layer_provider.addAttributes([QgsField("id",QVariant.Double)])
lavaka_layer.updateFields()
print (lavaka_layer.fields().names())

    # fill the field with the id's which are extracted from the names
    # (the name of the lavaka start with the id)
lavaka_layer.startEditing()
for feature in lavaka_layer.getFeatures():
     name = feature['Name']
     name_split = name.split("_")[0]
     feature['id'] = name_split
     lavaka_layer.updateFeature(feature)

################################################################################
#                  STEP 1: CREATE POINTS IN PRE-EROSION POLYGON 
################################################################################
# create a new folder called 'randomPoints' to the main folder. In this folder 
# the layers containing the random points will be stored

# add the layer to the map without plotting italic
QgsProject.instance().addMapLayer(poly_layer, False)

# loop through all the features of the polygon layer to get the correct ID's
# use i as an index to select each feature of the shapefile
i=0
for feature in poly_layer.getFeatures():
    ID=(feature['ID'])
    print(ID)
    poly_layer.select(i)
    #set input params
    params = {'INPUT':QgsProcessingFeatureSourceDefinition(poly_layer.id(), True),
              'STRATEGY':0,
              'EXPRESSION':' $area /20',
              'MIN_DISTANCE':1,
              'OUTPUT': path+'randomPoints/'+str(ID)+'_random_points.shp'}
    processing.run("qgis:randompointsinsidepolygons", params)
    #Remove the current selection and then pass to the next one
    poly_layer.removeSelection()
    i=i+1

################################################################################
#                  STEP 2: ASSIGN DEM-VALUES TO POINTS
################################################################################ 
# create a new folder called 'randomPointsDEM' to the main folder. In this folder 
# the layers containing the random points with assigned DEM values will be stored

# loop through all the files of folder randomPoints

for file in os.listdir(path+'randomPoints'):
     filename = os.fsdecode(file)
     # run the algorithm for all the .shp layers
     if filename.endswith(".shp"):
        print(filename)
        params = {'SHAPES':path+'randomPoints/'+filename,
                    'GRIDS':[DEM],
                    'RESAMPLING':0,
                    'RESULT': path+'randomPointsDEM/'+filename[0:-4]+'_DEM.shp'}
        processing.run("saga:addrastervaluestopoints",params)

################################################################################
#                  STEP 3: INTERPOLATE THE PRE-EROSION SURFACE
################################################################################
# Two interpolation methods are used: Spline and TIN interpolation.
# The method that will be applied to the data is set in the beginning of the script
# (interpol_method = 1 or 2. 1 = Spline, 2 = TIN).


# 1. SPLINE INTERPOLATION
    # Create a new folder called 'SPLINEinterpol' to the main folder. In this folder 
    # the layers containing the interpolated surfaces will be stored
    
    # 'zcolumn': Verify the name of the height attribute of the randomPointsDEM layer that
    # was created in the previous step, this name has to be filled in for 'zcolumn'
    
    # 'GRASS_REGION_CELLSIZE_PARAMETER': equal to the resolution of the DEM
    # (TanDEM-X: 12 m, SRTM: 30 m, UAV-SfM: 0.20 m)
    
if interpol_method == 1:
    # loop through all the files of folder randomPointsDEM
    for file in os.listdir(path+'randomPointsDEM'):
         filename = os.fsdecode(file)
         # run the algorithm for all the .shp layers
         if filename.endswith(".shp"):
            print(filename)
            # get the extend of the layer
            params = {'input':path +'randomPointsDEM/'+filename,
                      'zcolumn':'SRTM',
                      'where':'',
                      'mask':None,
                      'tension':40,
                      'smooth':None,
                      'smooth_column':None,
                      'segmax':40,
                      'npmin':300,
                      'dmin':None,
                      'dmax':None,
                      'zscale':1,
                      'theta':None,
                      'scalex':None,
                      '-t':False,
                      '-d':False,
                      'elevation':path+'SPLINEinterpol/'+ filename.split("_")[0]+'_spline.tif',
                      'aspect':'TEMPORARY_OUTPUT',
                      'pcurvature':'TEMPORARY_OUTPUT',
                      'tcurvature':'TEMPORARY_OUTPUT',
                      'mcurvature':'TEMPORARY_OUTPUT',
                      'deviations':'TEMPORARY_OUTPUT',
                      'treeseg':'TEMPORARY_OUTPUT',
                      'overwin':'TEMPORARY_OUTPUT',
                      'GRASS_REGION_PARAMETER':None,
                      'GRASS_REGION_CELLSIZE_PARAMETER':30.49,
                      'GRASS_RASTER_FORMAT_OPT':'',
                      'GRASS_RASTER_FORMAT_META':'',
                      'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
                      'GRASS_MIN_AREA_PARAMETER':0.0001,
                      'GRASS_OUTPUT_TYPE_PARAMETER':0,
                      'GRASS_VECTOR_DSCO':'',
                      'GRASS_VECTOR_LCO':'',
                      'GRASS_VECTOR_EXPORT_NOCAT':False}
            processing.run("grass7:v.surf.rst",params)

# 2. TIN interpolation
    # Create a new folder called 'TINinterpol' to the main folder. In this folder 
    # the layers containing the interpolated surfaces will be stored
    
    # 'PIXEL_SIZE = set to the pixel size of the DEM
    # (TanDEM-X: 12 m, SRTM: 30 m, UAV-SfM: 0.20 m)
    
if interpol_method == 2:
    # loop through all the files of folder randomPointsDEM
    for file in os.listdir(path+'randomPointsDEM'):
         filename = os.fsdecode(file)
         # run the algorithm for all the .shp layers
         if filename.endswith(".shp"):
            print(filename)
            # get the extend of the layer
            pointsDEM = QgsVectorLayer(path+'randomPointsDEM/'+filename, '', 'ogr')
            ext = pointsDEM.extent()
            xmin = ext.xMinimum()
            xmax = ext.xMaximum()
            ymin = ext.yMinimum()
            ymax = ext.yMaximum()
            params = {'INTERPOLATION_DATA':path +'randomPointsDEM/'+filename+'::~::0::~::1::~::0',
                        'METHOD':0,
                        'EXTENT':str(xmin)+','+str(xmax)+','+str(ymin)+','+str(ymax)+' [EPSG:32739]',
                        'PIXEL_SIZE':30.49,
                        'OUTPUT':path+'TINinterpol/'+ filename.split("_")[0]+'_interpol.tif'}
            processing.run("qgis:tininterpolation",params)

################################################################################
#                  STEP 4: CALCULATE ELEVATION DIFFERENCE
################################################################################
# substract the original DEM from the interpolated DEM to get the heigh difference

# import the necesarry toolboxes
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

# load the DEM layer
DEM_layer = QgsRasterLayer(DEM,"DEM_layer")
if not DEM_layer.isValid():
    print("DEM_layer failed to load!")
entries = []
boh2 = QgsRasterCalculatorEntry()
boh2.ref = 'boh2@1'
boh2.raster = DEM_layer
boh2.bandNumber = 1
entries.append( boh2 )

# folder names depend on the interpolation method
if interpol_method == 1:
     # Create a new folder called 'DEM_dif_SPLINE' to the main folder. In this folder 
     # the layers containing the DEM difference layers based on the SPLINE method will be stored
     inputFolder = path + 'SPLINEinterpol'
     outputFolder = path + 'DEM_dif_SPLINE/'

if interpol_method == 2:
     # Create a new folder called 'DEM_dif_TIN' to the main folder. In this folder 
     # the layers containing the DEM difference layers based on the TIN method will be stored
     inputFolder = path+'TINinterpol'
     outputFolder = path + 'DEM_dif_TIN/'

# loop through all the files of the folder in which the interpolation results
# are stored
for file in os.listdir(inputFolder):
     filename = os.fsdecode(file)
     # run the algorithm for all the .shp layers
     if filename.endswith(".tif"):
         print(filename)
         interpolLayer = QgsRasterLayer(inputFolder+'/'+filename,"interpolLayer")
         if not interpolLayer.isValid():
             print("interpolLayer failed to load!")
         boh1 = QgsRasterCalculatorEntry()
         boh1.ref = 'boh1@1'
         boh1.raster = interpolLayer
         boh1.bandNumber = 1
         entries.append( boh1 )
         # Process calculation with input extent and resolution
         calc = QgsRasterCalculator('(boh1@1 - boh2@1)',outputFolder+'/'+filename.split("_")[0]+'_DEM_dif.tif','GTiff', interpolLayer.extent(), interpolLayer.width(), interpolLayer.height(), entries )
         calc.processCalculation()
         #remove the latest added entry
         del entries [1]

################################################################################
#                  STEP 5: ELEVATION DIFFERENCE CLIPPED TO LAVAKA EXTENT
################################################################################
# folder names depend on the interpolation method
if interpol_method == 1:
    # Create a new folder called 'Clipped_SPLINE' to the main folder. In this folder 
    # the layers containing the clipped DEM difference layers based on the SPLINE method will be stored
    inputFolder = path + 'DEM_dif_SPLINE'
    outputFolder = path + 'Clipped_SPLINE/'
    
if interpol_method == 2:
    # Create a new folder called 'Clipped_TIN' to the main folder. In this folder 
    # the layers containing the clipped DEM difference layers based on the TIN method will be stored
    inputFolder = path + 'DEM_dif_TIN'
    outputFolder = path + 'Clipped_TIN/'

# loop through all the files of DEM dif (= all the files for which the polygons are drawn)

for file in os.listdir(inputFolder):
     filename = os.fsdecode(file)
     # run the algorithm for all the .shp layers
     if filename.endswith(".tif"):
        print(filename)
        ID1 = filename.split("_")[0]
        print(ID1)
        query = '"ID" = '+str(ID1)
        selection = lavaka_layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
        lavaka_layer.selectByIds([s.id() for s in selection])
        lavaka_layer.selectedFeatures()
        QgsProject.instance().addMapLayer(lavaka_layer, False)
        params = {'INPUT':inputFolder+'/'+filename,
                'POLYGONS':QgsProcessingFeatureSourceDefinition(lavaka_layer.id(), True),
                'OUTPUT':outputFolder+str(ID1)+'_DEMdif_clipped.sdat'}
        processing.run("saga:cliprasterwithpolygon",params)

################################################################################
#                  STEP 6: EXPORT RESULTS
################################################################################
# folder names depend on the interpolation method
if interpol_method == 1:
    # Create a new folder called 'ClippedRasterValues_SPLINE' to the main folder. In this folder 
    # the layers containing the unique value reports based on the SPLINE method will be stored
    inputFolder = path + 'Clipped_SPLINE'
    outputFolder = path+'ClippedRasterValues_SPLINE/'
    
if interpol_method == 2:
    # Create a new folder called 'ClippedRasterValues_TIN' to the main folder. In this folder 
    # the layers containing the clipped DEM difference layers based on the TIN method will be stored
    inputFolder = path + 'Clipped_TIN'
    outputFolder = path + 'ClippedRasterValues_TIN/'


for file in os.listdir(inputFolder):
     filename = os.fsdecode(file)
     # run the algorithm for all the .sdat layers
     if filename.endswith(".sdat"):
         print(filename)
         ID = filename.split("_")[0]
         print(ID)
         params = {'INPUT':inputFolder+'/'+filename,
         'BAND':1,
         'OUTPUT_HTML_FILE':outputFolder+ID+'_uniqueValues_report.html',
         'OUTPUT_TABLE':outputFolder+ID+'_uniqueValues_report.shp'}
         processing.run("native:rasterlayeruniquevaluesreport", params)