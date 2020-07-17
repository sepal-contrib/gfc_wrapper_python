import os


def create_folder(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname


################################################################
########                        folders                 ########
################################################################

def getDwnDir():
    pathname = os.path.join(os.path.expanduser('~'), 'downloads/gfc') + '/'
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
    pathname = os.path.join(getRootDir(), 'tmp') + '/'
    return create_folder(pathname)

def getGfcDir():
    pathname = os.path.join(getRootDir(), 'gfc') + '/'
    return create_folder(pathname)

def getAoiDir():
    pathname = os.path.join(getRootDir(), 'aoi') + '/'
    return create_folder(pathname)

def getStatDir():
    pathname = os.path.join(getRootDir(), 'stat') + '/'
    return create_folder(pathname)

def getMspaDir():
    pathname = os.path.join(getRootDir(), 'mspa') + '/'
    return create_folder(pathname)

def getTmpMspaDir():
    pathname = os.path.join(getRootDir(), 'tmp/mspa') + '/'
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

##########################################################
#########                     legend                ######
##########################################################

def getMyClasses():
    return [0, getMaxYear(), 30, 40, 50, 51]

def getMyLabel():
    return [
        "no data",
        "loss_{}".format(2000+getMaxYear()),
        "non forest",
        "forest",
        "gains",
        "gains+loss"
    ]

def getCodes():
    return {getMyClasses()[index]: value for index, value in enumerate(getMyLabel()) }

def getPalette():
    return [
        'yellow',
        'darkred', #loss
        'lightgrey', #non forest
        'darkgreen', #forest
        'lightgreen', #gain
        'black', #ndat
        'purple' #gnls
    ]