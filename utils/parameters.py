import os
import sys
sys.path.append("..") 
from utils import utils
import pandas as pd 
import matplotlib as mpl


def create_folder(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname

################################################################
########                        folders                 ########
################################################################

def getResultDir():
    pathname = os.path.join(os.path.expanduser('~'), 'gfc_wrapper_results') + '/'
    return create_folder(pathname)

def getDwnDir():
    pathname = os.path.join(getResultDir(), 'downloads') + '/'
    return create_folder(pathname) 

def getRootDir():
    pathname = os.path.join(os.path.expanduser('~'), 'gfc_wrapper_python') + '/'
    return create_folder(pathname) 

def getscriptDir():
    pathname = os.path.join(getRootDir(), 'scripts') + '/'
    return create_folder(pathname)

def getDataDir():
    pathname = os.path.join(getRootDir(), 'data') + '/'
    return create_folder(pathname)

def getTmpDir():
    pathname = os.path.join(getResultDir(), 'tmp') + '/'
    return create_folder(pathname)

def getGfcDir():
    pathname = os.path.join(getResultDir(), 'gfc') + '/'
    return create_folder(pathname)

def getAoiDir():
    pathname = os.path.join(getRootDir(), 'aoi') + '/'
    return create_folder(pathname)

def getStatDir():
    pathname = os.path.join(getResultDir(), 'stat') + '/'
    return create_folder(pathname)

def getMspaDir():
    pathname = os.path.join(getRootDir(), 'mspa') + '/'
    return create_folder(pathname)

def getTmpMspaDir():
    pathname = os.path.join(getResultDir(), 'tmp/mspa') + '/'
    return create_folder(pathname)

def getUtilsDir():
    pathname = os.path.join(getRootDir(), 'utils') + '/'
    return create_folder(pathname)

########################################################
##########              hard-coded params          #####
########################################################
def getMaxYear():
    return 19

def getSpacing():
    return 0.011

def getOffset():
    return 0.001

def getProj():
    return '+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m no_defs'

def getDataset():
    return "GFC-2019-v1.7"

def getClasses():
    return [100,50,40,30,20,10,5,4,3,2,1]

def getTypes():
    return ["treecover2000","lossyear","gain","datamask"]

def getDataset():
    return 'UMD/hansen/global_forest_change_2019_v1_7'

##########################################################
#########                     legend                ######
##########################################################

def getMyClasses():
    
    years = [i for i in range (1, getMaxYear()+1)]
    pos = 1
    my_classes = [0,30,40,50,51]
    my_classes[pos:pos] = years

    return my_classes

def getMyLabel():
    
    years = ['loss_{}'.format(str(2000+i)) for i in range (1, getMaxYear()+1)]
    labels = ["no data","non forest","forest","gains","gain+loss"]
    pos = 1
    labels[pos:pos] = years
    
    return labels

def getCodes():
    codes = [i for i in range(1, getMaxYear() + 1)] + [30, 40, 50, 51]
    codes = [str(i) for i in codes]
    
    return codes

def getSldStyle():
    #Define an SLD style of discrete intervals to apply to the image.
    
    # TODO can do it programatically
    sld_intervals = '<RasterSymbolizer>' 
    sld_intervals += '<ColorMap type="intervals" extended="false" >' 
    sld_intervals += '<ColorMapEntry color="#000000" quantity="0" label="no data"/>' 
    sld_intervals += '<ColorMapEntry color="#F9F200" quantity="1" label="loss-2001"/>' 
    sld_intervals += '<ColorMapEntry color="#DFF800" quantity="2" label="loss-2002"/>' 
    sld_intervals += '<ColorMapEntry color="#EDD700" quantity="3" label="loss-2003"/>' 
    sld_intervals += '<ColorMapEntry color="#E7C900" quantity="4" label="loss-2004"/>' 
    sld_intervals += '<ColorMapEntry color="#E0BC00" quantity="5" label="loss-2005"/>' 
    sld_intervals += '<ColorMapEntry color="#DAAE00" quantity="6" label="loss-2006"/>' 
    sld_intervals += '<ColorMapEntry color="#D4A100" quantity="7" label="loss-2007"/>' 
    sld_intervals += '<ColorMapEntry color="#CE9400" quantity="8" label="loss-2008"/>' 
    sld_intervals += '<ColorMapEntry color="#C88600" quantity="9" label="loss-2009"/>' 
    sld_intervals += '<ColorMapEntry color="#C27900" quantity="10" label="loss-2010"/>' 
    sld_intervals += '<ColorMapEntry color="#BC6B00" quantity="11" label="loss-2011"/>' 
    sld_intervals += '<ColorMapEntry color="#B65E00" quantity="12" label="loss-2012"/>' 
    sld_intervals += '<ColorMapEntry color="#B05100" quantity="13" label="loss-2013"/>' 
    sld_intervals += '<ColorMapEntry color="#AA4300" quantity="14" label="loss-2014"/>' 
    sld_intervals += '<ColorMapEntry color="#A33600" quantity="15" label="loss-2015"/>' 
    sld_intervals += '<ColorMapEntry color="#9D2800" quantity="16" label="loss-2016"/>' 
    sld_intervals += '<ColorMapEntry color="#971B00" quantity="17" label="loss-2017"/>' 
    sld_intervals += '<ColorMapEntry color="#910D00" quantity="18" label="loss-2018"/>' 
    sld_intervals += '<ColorMapEntry color="#8B0000" quantity="19" label="loss-2019"/>' 
    sld_intervals += '<ColorMapEntry color="#D3D3D3" quantity="30" label="non forest"/>' 
    sld_intervals += '<ColorMapEntry color="#006400" quantity="40" label="stable forest"/>' 
    sld_intervals += '<ColorMapEntry color="#800080" quantity="51" label="gain + loss"/>' 
    sld_intervals += '</ColorMap>'
    sld_intervals += '</RasterSymbolizer>'
    
    return sld_intervals

def getColorTable():
    
    pathname = getTmpDir() + 'color_table.txt'
    
    if not os.path.isfile(pathname):
        
        length = len(getMyClasses())
        color_r = {}
        color_g = {}
        color_b = {}
        
        color_r[0], color_g[0], color_b[0] = mpl.colors.to_rgb('black') #no data
        for i in range(1, getMaxYear()+1):
            color_r[i], color_g[i], color_b[i], _ = utils.colorFader(i)
        color_r[30], color_g[30], color_b[30] = mpl.colors.to_rgb('lightgrey') #non forest
        color_r[40], color_g[40], color_b[40] = mpl.colors.to_rgb('darkgreen') #forest
        color_r[50], color_g[50], color_b[50] = mpl.colors.to_rgb('lightgreen') #gains
        color_r[51], color_g[51], color_b[51] = mpl.colors.to_rgb('purple') #gain + loss
        
        color_r = [int(round(color_r[idx]*255)) for idx in color_r.keys()]
        color_g = [int(round(color_g[idx]*255)) for idx in color_g.keys()]
        color_b = [int(round(color_b[idx]*255)) for idx in color_b.keys()]
        
        color_table = pd.DataFrame({'classes':getMyClasses(), 'red': color_r, 'green': color_g, 'blue': color_b})
        
        color_table.to_csv(pathname, header=False, index=False, sep=' ')
    
    return pathname