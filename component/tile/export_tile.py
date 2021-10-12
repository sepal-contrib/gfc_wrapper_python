from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su

from component.message import cm
from component import scripts as cs


class ExportTile(sw.Tile):
    def __init__(self, model, aoi_model):

        # gather models
        self.model = model
        self.aoi_model = aoi_model

        # create a result tile
        self.result_tile = sw.Tile("gfc_export_tile", "Results", inputs=[""])

        super().__init__(
            "gfc_export_tile",
            "Export the data",
            btn=sw.Btn("Export data"),
            alert=sw.Alert(),
            inputs=[sw.Markdown(cm.gfc.txt)],
        )

        # add js behaviour
        self.btn.on_event("click", self._on_click)

    @su.loading_button(debug=True)
    def _on_click(self, widget, event, data):

        # check inputs
        if not self.alert.check_input(self.aoi_model.name, cm.gfc.no_aoi):
            return
        if not self.alert.check_input(self.model.threshold, cm.gfc.no_threshold):
            return
        if not self.alert.check_input(self.model.visualization, cm.gfc.no_viz):
            return

        # retreive the data
        self.clip_map, csv_file, result_layout = cs.gfc_export(
            self.aoi_model, self.model.threshold, self.alert
        )

        self.result_tile.set_content(result_layout)

        return
