from pathlib import Path

# this directory is the root directory of all sepal dashboard app.
# please make sure that any result that you produce is embeded inside this folder
# create a folder adapted to your need inside this folder to save anything in sepal
module_dir = Path("~", "module_results").expanduser()
module_dir.mkdir(exist_ok=True)

result_dir = module_dir / "gfc_wrapper"
result_dir.mkdir(exist_ok=True)

dow_dir = Path().home() / "downloads"


def create_result_folder(aoi_model):
    """Create a folder to download the glad images

    Args:
        aoi_model(aoiModel) : the model aoi

    Returns:
        glad_dir (path): pathname to the glad_result folder
    """
    aoi = aoi_model.name

    aoi_dir = result_dir / aoi
    aoi_dir.mkdir(exist_ok=True)

    return aoi_dir
