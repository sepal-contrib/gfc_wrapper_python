from sepal_ui import model
from traitlets import Any

class VizModel(model.Model):
    
    # set up your inputs
    threshold = Any(30).tag(sync=True)
    
    # set up output
    previous_asset_name = Any(None).tag(sync=True)
    visualization = Any(False).tag(sync=True)
    
    #set up output
    clip_map = Any(None).tag(sync=True)