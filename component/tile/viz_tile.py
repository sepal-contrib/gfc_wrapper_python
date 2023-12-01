from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
from sepal_ui.scripts import utils as su
import ipyvuetify as v

from component import parameter as cp
from component.message import cm
from component import scripts as cs


class VizTile(sw.Tile):
    def __init__(self, model, aoi_model):
        # gather model inputs
        self.model = model
        self.aoi_model = aoi_model

        # define widgets
        w_years = v.RangeSlider(
            label="Years",
            class_="mt-5",
            thumb_label="always",
            min=2000 + cp.gfc_min_year,
            max=2000 + cp.gfc_max_year,
        )
        w_years.v_model = [w_years.min, w_years.max]
        w_threshold = v.Slider(
            label="Threshold", class_="mt-5", thumb_label="always", v_model=30
        )

        # the btn and alert are created separately and linked after the call to super
        btn = sw.Btn("Update map", icon="mdi-check")
        alert = sw.Alert()

        # bind the widgets
        (self.model.bind(w_threshold, "threshold").bind(w_years, "years"))

        # create a map
        self.m = sm.SepalMap()
        self.m.layout.height = "80vh"

        legend_dict = dict(zip(cp.gfc_labels, cp.hex_palette))

        self.m.add_legend(legend_dict=legend_dict, position="topleft")

        # create a layout to display the map and the inputs side by side
        w_inputs = v.Layout(
            row=True,
            xs12=True,
            children=[
                v.Flex(
                    class_="pr-5 pt-5",
                    md4=True,
                    children=[w_years, w_threshold, btn, alert],
                ),
                v.Flex(md8=True, children=[self.m]),
            ],
        )

        super().__init__("gfc_map_tile", "GFC visualization", inputs=[w_inputs])

        # rewire btn and alert
        self.btn = btn
        self.alert = alert

        # bind js events
        self.btn.on_event("click", self._on_click)

    @su.loading_button()
    def _on_click(self, widget, event, data):
        # set viz to false if asset has changed
        self.model.visualization = self.model.previous_asset_name == self.aoi_model.name

        self.model.previous_asset_name = self.aoi_model.name

        # check inputs
        if not self.alert.check_input(self.aoi_model.name, cm.gfc.no_aoi):
            return
        if not self.alert.check_input(self.model.threshold, cm.gfc.no_threshold):
            return

        # display the results
        cs.display_gfc_map(self.aoi_model, self.model, self.m, self.alert)

        # validate the visualization process
        self.model.visualization = True

        return
