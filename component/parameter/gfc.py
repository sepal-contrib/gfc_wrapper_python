gfc_min_year = 1
gfc_max_year = 24
gfc_dataset = "UMD/hansen/global_forest_change_2024_v1_12"

gfc_classes = [0] + [i for i in range(1, gfc_max_year + 1)] + [30, 40, 50, 51]

gfc_labels = ["loss {}".format(str(2000 + i)) for i in range(1, gfc_max_year + 1)] + [
    "non forest",
    "forest",
    "gains",
    "gain+loss",
]

gfc_codes = [str(j) for j in [i for i in range(1, gfc_max_year + 1)] + [30, 40, 50, 51]]
