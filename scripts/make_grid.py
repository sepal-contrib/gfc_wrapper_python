import geopandas as gpd
import pandas as pd

def make_grid():
    
    #create the basegrid 
    
    ##################
    ### TODO        ##
    ##################
    gdf #as geo data frame
    
    #extract the data from the gdf
    df
    
    #create a dataset containing all levels of longitude
    lng = np.unique(df[['xcoord']].to_numpy())
    lon_fact = pd.DataFrame({
        'xccord': lng, 
        'lon_fact': [i for i in range(1, len(lng)+1)]
    }) 
    
    #create a dataset containing all levels of latitude
    lat = np.unique(df[['ycoord']].to_numpy())
    lat_fact = pd.DataFrame({
        'ycoord': lat, 
        'lat_fact': [i for i in range(1, len(lat)+1)]
    })
    
    #add these columns to gdf 
    pd.merge(df, lon_fact, on='xcoord')
    pd.merge(df, lat_fact, on='ycoord')
    
    df.columns = [
        'latitude',
        'longitude',
        'code',
        'lon_fact',
        'lat_fact'
    ]
    
    
    #esrimate the treecover for each year for each intensity level
    years = [i for i in range(1, pm.getMaxYear()+1)]
    classes = pm.getClasses()
    tcover = treecover_area.values
    out = [[utils.estimate(class_, year, df)*tcover for year in years] for class_ in classes]
    out = pd.DataFrame(out)
    
    #apply function estimate to cumulated years for all sub-sampling
    out['all_years'] = pd.DataFrame([utils.allEstimate(class_, df) for class_ in classes])
    
    # Add a column with number of samples corresponding to each level
    out['intensity'] = pd.DataFrame([utils.nombre(class_, df) for class_ in classes])
    
    #add column names 
    labels = ['year_{}'.format(str(2000+i)) for i in years] + ['total'] + ['intensity']
    
    out.columns = labels
    
    # Create, to the same format, a line corresponding to target areas of loss
    # The last number corresponds to column "intensity", with the number of pixels used
    
    
    #########################
    ## TODO qui est hist ? ##
    #########################
    
    resx_proj = resx * 111321
    
    loss_year = hist[(hist['code'] > 0) & (hist['code'] < 30)]
    loss_year = list(utils.toHectar(loss_year['pixels'], resx_proj).values)
    loss_area = list(lossarea.values)
    total = hist[
        (hist['code'] == 40)
        | ((hist['code'] > 0) & (hist['code'] < 30))
    ]
    total = list(total['pixel'].sum().values)
    final_line = loss_year + loss_area + total
    
    out.append(final_line)
    
    return out
    
    
    
    
            
            
    
    


"""
###############################################################################
################### GET THE BASE GRID
###############################################################################
samplepoints              <- SpatialPoints(makegrid(aoi,
                                                    cellsize=spacing,
                                                    offset = c(offset,offset)
                                                    ))
proj4string(samplepoints) <- proj4string(aoi)
pts                       <- samplepoints[aoi,]

spdf         <- SpatialPointsDataFrame(coords = pts@coords,
                                       data   = data.frame(pts),
                                       proj4string = CRS(proj4string(pts)))

names(spdf)  <- c("xcoord","ycoord")

spdf$code    <- extract(raster(paste0(tmp_dir,"tmp_gfc_map_",countrycode,".tif")),
                        spdf)
df <- spdf@data

################# Create a new dataset containing all levels of longitude
lon_fact <- data.frame(
  cbind(
    levels(as.factor(df$xcoord)),
    1:length(levels(as.factor(df$xcoord)))
  )
)

################# Create a new dataset containing all levels of latitude
lat_fact <- data.frame(
  cbind(
    levels(as.factor(df$ycoord)),
    1:length(levels(as.factor(df$ycoord)))
  )
)

################# Add both columns to df
df<-merge(df,lon_fact,by.x = "xcoord",by.y='X1')
df<-merge(df,lat_fact,by.x = "ycoord",by.y='X1')

names(df)<-c("latitude",
             "longitude",
             "code",
             "lon_fact",
             "lat_fact")

df$lon_fact <- as.numeric(df$lon_fact)
df$lat_fact <- as.numeric(df$lat_fact)


out <- data.frame(
  sapply(1:max_year,function(y){
    sapply(classes,function(x){
      estimate(x,y)*tcov_area
    })
  })
)

################# Apply function estimate to cumulated years for all sub-sampling
out$all_years <- sapply(classes,function(x){
  all_estimate(x)*tcov_area
})

################# Change names
names(out)<-c(paste("year",2000+(1:max_year),sep="_"),"total")

################# Add a column with number of samples corresponding to each level
out$intensity <- sapply(classes,function(x){nombre(x)})

################# Create, to the same format, a line corresponding to target areas of loss
################# The last number corresponds to column "intensity", with the number of pixels used
out[length(classes)+1,] <- c(hist[(hist$code > 0 & hist$code < 30),"pixels"]*pixel*pixel/10000,
                             loss_area,
                             sum(hist[(hist$code == 40 | (hist$code > 0 & hist$code < 30)),"pixels"]))
                             """