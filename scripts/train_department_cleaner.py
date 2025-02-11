# %%
import joblib
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from skrub import TextEncoder
from unidecode import unidecode

DEPARTMENT_MAPPING = {
    "ain": "01",
    "aisne": "02",
    "allier": "03",
    "alpes-de-haute-provence": "04",
    "hautes-alpes": "05",
    "alpes-maritimes": "06",
    "ardèche": "07",
    "ardennes": "08",
    "ariège": "09",
    "aube": "10",
    "aude": "11",
    "aveyron": "12",
    "bouches-du-rhône": "13",
    "calvados": "14",
    "cantal": "15",
    "charente": "16",
    "charente-maritime": "17",
    "cher": "18",
    "corrèze": "19",
    "corse-du-sud": "2a",
    "haute-corse": "2b",
    "côte-d'or": "21",
    "côtes-d'armor": "22",
    "creuse": "23",
    "dordogne": "24",
    "doubs": "25",
    "drôme": "26",
    "eure": "27",
    "eure-et-loir": "28",
    "finistère": "29",
    "gard": "30",
    "haute-garonne": "31",
    "gers": "32",
    "gironde": "33",
    "hérault": "34",
    "ille-et-vilaine": "35",
    "indre": "36",
    "indre-et-loire": "37",
    "isère": "38",
    "jura": "39",
    "landes": "40",
    "loir-et-cher": "41",
    "loire": "42",
    "haute-loire": "43",
    "loire-atlantique": "44",
    "loiret": "45",
    "lot": "46",
    "lot-et-garonne": "47",
    "lozère": "48",
    "maine-et-loire": "49",
    "manche": "50",
    "marne": "51",
    "haute-marne": "52",
    "mayenne": "53",
    "meurthe-et-moselle": "54",
    "meuse": "55",
    "morbihan": "56",
    "moselle": "57",
    "nièvre": "58",
    "nord": "59",
    "oise": "60",
    "orne": "61",
    "pas-de-calais": "62",
    "puy-de-dôme": "63",
    "pyrénées-atlantiques": "64",
    "hautes-pyrénées": "65",
    "pyrénées-orientales": "66",
    "bas-rhin": "67",
    "haut-rhin": "68",
    "rhône": "69",
    "haute-saône": "70",
    "saône-et-loire": "71",
    "sarthe": "72",
    "savoie": "73",
    "haute-savoie": "74",
    "paris": "75",
    "seine-maritime": "76",
    "seine-et-marne": "77",
    "yvelines": "78",
    "deux-sèvres": "79",
    "somme": "80",
    "tarn": "81",
    "tarn-et-garonne": "82",
    "var": "83",
    "vaucluse": "84",
    "vendée": "85",
    "vienne": "86",
    "haute-vienne": "87",
    "vosges": "88",
    "yonne": "89",
    "territoire-de-belfort": "90",
    "essonne": "91",
    "hauts-de-seine": "92",
    "seine-saint-denis": "93",
    "val-de-marne": "94",
    "val-d'oise": "95",
    # Overseas departments
    "guadeloupe": "971",
    "martinique": "972",
    "guyane": "973",
    "la réunion": "974",
    "mayotte": "976",
}


def train_department_cleaner():
    reference_texts = []
    codes = []

    for name, code in DEPARTMENT_MAPPING.items():
        variations = [
            name,
            name.replace("-", " "),
            name.upper(),
            f"département {name}",
            f"dept {name}",
            f"{name} ({code})",
            f"{code}",
            f"département {code}",
            # Remove diacritics version
            unidecode(name),
            # Common abbreviations
            f"dept. {code}",
            f"dép. {name}",
        ]
        reference_texts.extend(variations)
        codes.extend([code] * len(variations))

    reference_texts = pd.Series(reference_texts)
    codes = pd.Series(codes)

    model = make_pipeline(
        TextEncoder(model_name="all-MiniLM-L6-v2", device="cpu"),
        KNeighborsClassifier(n_neighbors=1, metric="cosine"),
    ).fit(reference_texts, codes)

    return model


if __name__ == "__main__":
    model = train_department_cleaner()
    joblib.dump(model, "model/department_clearner.joblib")
