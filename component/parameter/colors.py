from matplotlib import colors
import numpy as np

from .gfc import gfc_max_year, gfc_classes


def color_fader(v=0):
    """return a rgb (0-255) tuple corresponding the v value in a 19 spaces gradient between yellow and darkred"""

    c1 = "yellow"
    c2 = "darkred"

    n = len(range(1, gfc_max_year + 1))
    mix = v / n

    c1 = np.array(colors.to_rgb(c1))
    c2 = np.array(colors.to_rgb(c2))

    return (1 - mix) * c1 + mix * c2


# colors
gfc_colors = {}
for i in range(1, gfc_max_year + 1):
    gfc_colors["{} loss".format(2000 + i)] = colors.to_rgba(color_fader(i))
gfc_colors["non forest"] = colors.to_rgba("lightgrey")
gfc_colors["forest"] = colors.to_rgba("darkgreen")
gfc_colors["gains"] = colors.to_rgba("lightgreen")
gfc_colors["gain + loss"] = colors.to_rgba("purple")

# sld
color_map_entry = '\n<ColorMapEntry color="{0}" quantity="{1}" label="{2}"/>'

sld_intervals = "<RasterSymbolizer>"
sld_intervals += '\n<ColorMap type="intervals" extended="false" >'
sld_intervals += color_map_entry.format(colors.to_hex("black").upper(), 0, "no data")
for i in range(1, gfc_max_year + 1):
    sld_intervals += color_map_entry.format(
        colors.to_hex(color_fader(i)).upper(), i, "loss-" + str(2000 + i)
    )
sld_intervals += color_map_entry.format(
    colors.to_hex("lightgrey").upper(), 30, "non forest"
)
sld_intervals += color_map_entry.format(
    colors.to_hex("darkgreen").upper(), 40, "stable forest"
)
sld_intervals += color_map_entry.format(colors.to_hex("lightgreen").upper(), 50, "gain")
sld_intervals += color_map_entry.format(
    colors.to_hex("purple").upper(), 51, "gain + loss"
)
sld_intervals += "\n</ColorMap>"
sld_intervals += "\n</RasterSymbolizer>"

# hex palette
hex_palette = []

# hex_palette.append(colors.to_hex('black')) #no data
for i in range(1, gfc_max_year + 1):
    hex_palette.append(colors.to_hex(color_fader(i)))  # year loss
hex_palette.append(colors.to_hex("lightgrey"))  # non forest
hex_palette.append(colors.to_hex("darkgreen"))  # forest
hex_palette.append(colors.to_hex("lightgreen"))  # gains
hex_palette.append(colors.to_hex("purple"))  # gain + loss

# color table
length = len(gfc_classes)
color_r = {}
color_g = {}
color_b = {}

color_r[0], color_g[0], color_b[0] = colors.to_rgb("black")  # no data
for i in range(1, gfc_max_year + 1):
    color_r[i], color_g[i], color_b[i] = colors.to_rgb(color_fader(i))
color_r[30], color_g[30], color_b[30] = colors.to_rgb("lightgrey")  # non forest
color_r[40], color_g[40], color_b[40] = colors.to_rgb("darkgreen")  # forest
color_r[50], color_g[50], color_b[50] = colors.to_rgb("lightgreen")  # gains
color_r[51], color_g[51], color_b[51] = colors.to_rgb("purple")  # gain + loss

color_table = {
    k: (int(color_r[k] * 255), int(color_g[k] * 255), int(color_b[k] * 255), 255)
    for k in color_r.keys()
}
