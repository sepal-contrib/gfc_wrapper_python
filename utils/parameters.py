import os
import sys
sys.path.append("..") 
from utils import utils
import pandas as pd 
from matplotlib import colors


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
    labels = years + ["non forest","forest","gains","gain+loss"]
    
    return labels

def getCodes():
    codes = [i for i in range(1, getMaxYear() + 1)] + [30, 40, 50, 51]
    codes = [str(i) for i in codes]
    
    return codes

def getSldStyle():
    #Define an SLD style of discrete intervals to apply to the image.
    color_map_entry = '\n<ColorMapEntry color="{0}" quantity="{1}" label="{2}"/>' 
    
    # TODO can do it programatically
    sld_intervals = '<RasterSymbolizer>' 
    sld_intervals += '\n<ColorMap type="intervals" extended="false" >' 
    
    sld_intervals += color_map_entry.format(colors.to_hex('black').upper(), 0, 'no data')
    for i in range(1, getMaxYear()+1):
        sld_intervals += color_map_entry.format(colors.to_hex(utils.colorFader(i)).upper(), i, 'loss-' + str(2000+i))
    sld_intervals += color_map_entry.format(colors.to_hex('lightgrey').upper(), 30, 'non forest')
    sld_intervals += color_map_entry.format(colors.to_hex('darkgreen').upper(), 40, 'stable forest')
    sld_intervals += color_map_entry.format(colors.to_hex('lightgreen').upper(), 50, 'gain')
    sld_intervals += color_map_entry.format(colors.to_hex('purple').upper(), 51, 'gain + loss')
                                            
    sld_intervals += '\n</ColorMap>'
    sld_intervals += '\n</RasterSymbolizer>'    
    
    return sld_intervals

def getColorTable():
    
    pathname = getTmpDir() + 'color_table.txt'
    
    if not os.path.isfile(pathname):
        
        length = len(getMyClasses())
        color_r = {}
        color_g = {}
        color_b = {}
        
        color_r[0], color_g[0], color_b[0] = colors.to_rgb('black') #no data
        for i in range(1, getMaxYear()+1):
            color_r[i], color_g[i], color_b[i] = colors.to_rgb(utils.colorFader(i))
        color_r[30], color_g[30], color_b[30] = colors.to_rgb('lightgrey') #non forest
        color_r[40], color_g[40], color_b[40] = colors.to_rgb('darkgreen') #forest
        color_r[50], color_g[50], color_b[50] = colors.to_rgb('lightgreen') #gains
        color_r[51], color_g[51], color_b[51] = colors.to_rgb('purple') #gain + loss
        
        color_r = [int(round(color_r[idx]*255)) for idx in color_r.keys()]
        color_g = [int(round(color_g[idx]*255)) for idx in color_g.keys()]
        color_b = [int(round(color_b[idx]*255)) for idx in color_b.keys()]
        
        color_table = pd.DataFrame({'classes':getMyClasses(), 'red': color_r, 'green': color_g, 'blue': color_b})
        
        color_table.to_csv(pathname, header=False, index=False, sep=' ')
    
    return pathname