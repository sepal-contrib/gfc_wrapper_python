#####################
import ee
import rasterio as rio
from rasterio.merge import merge
import ipyvuetify as v
from sepal_ui import color as sc
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw

from component import parameter as cp

from . import compute_areas as ca
from .gdrive import gdrive
from . import gee


from sepal_ui.mapping import SepalMap

ee.Initialize()


def display_gfc_map(aoi_model, model, m: SepalMap, alert):
    alert.add_live_msg("Loading tiles")

    # use aoi_name
    aoi_name = aoi_model.name

    # load the gfc map
    gfc_map = ca.compute_ee_map(aoi_model, model)

    # load the aoi
    aoi = aoi_model.feature_collection

    if not model.visualization:
        # Create an empty image into which to paint the features, cast to byte.
        empty = ee.Image().byte()
        # Paint all the polygon edges with the same number and width, display.
        outline = empty.paint(**{"featureCollection": aoi, "color": 1, "width": 3})
        m.addLayer(outline, {"palette": sc.info}, "aoi")

        # zoom on the aoi
        m.zoom_ee_object(aoi.geometry())

        # empty all the previous gfc masks
        for layer in m.layers:
            if "gfc_" in layer.name:
                m.remove_layer(layer)

    # add the values to the map
    layer_name = f"gfc_{model.threshold}_{model.years[0]:.0f}_{model.years[1]:.0f}"
    if not m.find_layer(layer_name, none_ok=True):
        m.addLayer(gfc_map.sldStyle(cp.sld_intervals), {}, layer_name)
        message = "Tiles loaded"
    else:
        message = "Tiles were already on the map"

    alert.add_live_msg(message, "success")

    return


def gfc_export(aoi_model, model, alert):
    threshold = model.threshold
    start = int(model.years[0])
    end = int(model.years[1])

    # use aoi_name
    aoi_name = aoi_model.name

    # load the map
    aoi = aoi_model.feature_collection
    gfc_map = ca.compute_ee_map(aoi_model, model)

    # generate the result folder
    result_dir = cp.result_dir / aoi_name
    result_dir.mkdir(exist_ok=True)

    ############################
    ###    create tif file   ###
    ############################

    # skip if output already exist
    id_ = f"{threshold}_{start}_{end}"
    alert.add_live_msg("Creating the map")
    clip_map = result_dir / f"{id_}_merged_gfc_map.tif"
    clip_legend = result_dir / f"{id_}_gfc_legend.pdf"

    ca.export_legend(clip_legend)

    if clip_map.is_file():
        alert.add_live_msg("Gfc map threshold already performed", "success")
    else:
        task_name = f"{aoi_name}_{id_}_gfc_map"

        # launch the gee task
        drive_handler = gdrive()

        if drive_handler.get_files(task_name) == []:
            # launch the exportation of the map
            task_config = {
                "image": gfc_map,
                "description": task_name,
                "scale": 30,
                "region": aoi.geometry(),
                "maxPixels": 1e12,
            }

            task = ee.batch.Export.image.toDrive(**task_config)
            task.start()

            # wait for the task
            gee.wait_for_completion(task_name, alert)

        alert.add_live_msg("start downloading to Sepal")

        # download to sepal
        files = drive_handler.get_files(task_name)
        drive_handler.download_files(files, result_dir)

        # merge the tiles together
        tmp_clip_map = result_dir / f"{id_}_tmp_merged_gfc_map.tif"
        file_pattern = f"{task_name}*.tif"

        src_files = [f for f in result_dir.glob(file_pattern)]
        src_files_rio = [rio.open(f) for f in src_files]

        mosaic, out_trans = merge(src_files_rio)

        out_meta = src_files_rio[0].meta.copy()

        # Update the metadata
        out_meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": out_trans,
            }
        )

        with rio.open(clip_map, "w", **out_meta) as dest:
            dest.write(mosaic)
            dest.write_colormap(1, cp.color_table)

        # close the files
        [f.close() for f in src_files_rio]

        # delete the tmp_files
        [f.unlink() for f in src_files]

        # delete the gdrive files
        drive_handler.delete_files(files)

    alert.add_live_msg("Downloaded to Sepal", "success")

    alert.add_live_msg("Create histogram")

    ############################
    ###    create txt file   ###
    ############################

    csv_file = result_dir / f"{id_}_gfc_stat.csv"
    hist = ca.create_hist(result_dir, clip_map, alert)

    if csv_file.is_file():
        alert.add_live_msg("histogram already created", "success")
    else:
        hist.to_csv(csv_file, index=False)
        alert.add_live_msg("Histogram created", "success")

    #################################
    ###    create sum-up layout   ###
    #################################

    fig = ca.plot_loss(hist, aoi_name)

    table = ca.area_table(hist)

    m = sm.SepalMap()
    m.layout.height = "85vh"

    legend_dict = dict(zip(cp.gfc_labels, cp.hex_palette))

    m.add_legend(legend_dict=legend_dict, position="topleft")
    m.zoom_ee_object(aoi.geometry())
    m.addLayer(gfc_map.sldStyle(cp.sld_intervals), {}, "gfc")
    outline = ee.Image().byte().paint(featureCollection=aoi, color=1, width=3)
    m.addLayer(outline, {"palette": sc.info}, "aoi")

    # create the partial layout
    partial_layout = v.Layout(
        Row=True,
        align_center=True,
        class_="pa-0 mt-5",
        children=[
            v.Flex(xs12=True, md6=True, class_="pa-0", children=[table, fig]),
            v.Flex(xs12=True, md6=True, class_="pa-0", children=[m]),
        ],
    )

    # create the links
    gfc_download_csv = sw.DownloadBtn("GFC hist values in .csv", path=csv_file)
    gfc_download_tif = sw.DownloadBtn("GFC raster in .tif", path=clip_map)
    gfc_download_pdf = sw.DownloadBtn("GFC legend in .pdf", path=clip_legend)

    # create the display
    children = [
        v.Layout(
            Row=True, children=[gfc_download_csv, gfc_download_tif, gfc_download_pdf]
        ),
        partial_layout,
    ]

    alert.add_live_msg("Export complete", "success")
    alert.append_msg(
        "The statistic computations are run in the World Mollweide (ESRI:54009) projection.",
        True,
        "success",
    )

    return (clip_map, csv_file, children)
