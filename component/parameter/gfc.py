gfc_max_year = 20
gfc_dataset = "UMD/hansen/global_forest_change_2020_v1_8"

gfc_classes = [0] + [i for i in range(1, gfc_max_year + 1)] + [30, 40, 50, 51]

gfc_labels = ["loss_{}".format(str(2000 + i)) for i in range(1, gfc_max_year + 1)] + [
    "non forest",
    "forest",
    "gains",
    "gain+loss",
]

gfc_codes = [str(j) for j in [i for i in range(1, gfc_max_year + 1)] + [30, 40, 50, 51]]
