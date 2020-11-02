STATUS = "Status: {}"

##########################################
###              gfc process           ###
##########################################
GFC_MAP = 'Click on "Update map" to visualize the data'
GFC_HIST = 'Click on "Compute areas" to analyse the gfc data on your selected aoi. The process can take several minutes.'
GFC_EXPORT = 'Click on "Export" to export the data to your sepal folder. The process can take time.'
EXPORT_MESSAGE = 'Click on "Export" to export the data'
NO_THRESHOLD = 'No threshold have been selected'
NO_AOI = 'No aoi have been provided, select one in step 1'
NO_VIZ= 'Before launching the export, it is strongly advised to vizualize data'
GFC_TXT = """
Considering the Aoi selected in step 1 and the threshold selected in step 2 the module will generate a combination of the GFC layers to produce a forest change map, for a given canopy cover threshold. It will live in a ~/gfc_wrapper_results folder of your sepal environment.  
2 results will be produced:  
  
- the map of the forest change mask using the color tab presented in the interactive maps (.tif)
- the legend of the raster (.pdf)
- the distribution of each defined zone (.csv)
"""


#########################################
###          MSPA process             ###
#########################################
MSPA_MESSAGE = 'Click on "Run process" to launch the process on your sepal account'
NO_MAP = 'No map have been provided, compute the GFC analysis first'
NO_INPUT ='Missing input for the process, complete all fields'
