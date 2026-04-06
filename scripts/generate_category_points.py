from __future__ import annotations

import io
import json
import os
import warnings

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SHEET_ID = "1DCkhgN08_uEqpTTntl5_1iDjcXM_yaJc"

SHEET_NAMES = [
    "Catégorie_2",
    "Catégorie_3",
    "Catégorie_4",
    "Catégorie_5",
    "Catégorie_6",
    "Catégorie_F",
    "Catégorie_MG",
    "Catégorie_MF",
]

COL_IDENTITY = "Identité"
COL_POINTS = "Total points"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _download_spreadsheet_excel(service_account_info: dict) -> io.BytesIO:
    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=credentials)
    request = drive_service.files().get_media(fileId=SHEET_ID)
    file_handle = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handle, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    file_handle.seek(0)
    return file_handle


def _read_category_sheet(
    file_handle: io.BytesIO, sheet_name: str
) -> pd.DataFrame | None:
    """Load one worksheet; row 4 (1-based) is the header row."""
    try:
        file_handle.seek(0)
        df = pd.read_excel(
            file_handle,
            sheet_name=sheet_name,
            header=0,
            skiprows=3,
            engine="openpyxl",
        )
    except (ValueError, KeyError):
        return None
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _tab_slug(sheet_name: str) -> str:
    if "_" in sheet_name:
        tail = sheet_name.split("_", 1)[1]
    else:
        tail = sheet_name
    tail = tail.lower().replace("_", "-")
    return f"categorie-{tail}"


def _tab_label(sheet_name: str) -> str:
    return sheet_name.replace("_", " ")


def _strip_licence_prefix(raw: str) -> str:
    s = str(raw).strip()
    if not s:
        return ""
    if "-" in s:
        return s.split("-", 1)[1].strip()
    return s


def _format_prenom(s: str) -> str:
    """Prénom: capitalize each word; support hyphenated parts (e.g. Jean-Pierre)."""
    parts: list[str] = []
    for w in s.split():
        if "-" in w:
            parts.append("-".join(p.capitalize() for p in w.split("-") if p))
        else:
            parts.append(w.capitalize())
    return " ".join(parts)


def _parse_nom_prenom(raw: str) -> tuple[str, str]:
    """Split NOM (all-caps tokens) from prénom (the rest), after optional « NN- » prefix."""
    body = _strip_licence_prefix(raw)
    if not body:
        return ("", "")
    words = body.split()
    if not words:
        return ("", "")

    nom_words: list[str] = []
    i = 0
    while i < len(words) and words[i].isupper():
        nom_words.append(words[i])
        i += 1

    if not nom_words:
        nom_words = [words[0].upper()]
        i = 1

    prenom_raw = " ".join(words[i:])
    nom = " ".join(w.upper() for w in nom_words)
    prenom = _format_prenom(prenom_raw) if prenom_raw else ""
    return (nom, prenom)


def _prepare_category_df(df: pd.DataFrame) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    col_id = None
    col_pts = None
    for c in df.columns:
        c_stripped = str(c).strip()
        if c_stripped == COL_IDENTITY:
            col_id = c
        if c_stripped == COL_POINTS:
            col_pts = c
    if col_id is None or col_pts is None:
        return None
    out = df[[col_id, col_pts]].copy()
    out.columns = [COL_IDENTITY, COL_POINTS]
    out[COL_IDENTITY] = out[COL_IDENTITY].astype(str).str.strip()
    out = out[out[COL_IDENTITY].ne("") & out[COL_IDENTITY].ne("nan")]
    out[COL_POINTS] = pd.to_numeric(out[COL_POINTS], errors="coerce")
    out = out[out[COL_POINTS].notna()]
    if out.empty:
        return None
    parsed = out[COL_IDENTITY].map(_parse_nom_prenom)
    out["_nom"] = parsed.map(lambda t: t[0])
    out["_prenom"] = parsed.map(lambda t: t[1])
    out = out[out["_nom"].str.len() > 0]
    out = out.sort_values(COL_POINTS, ascending=False)
    out["_rang"] = out[COL_POINTS].rank(method="min", ascending=False).astype(int)
    return out


def _generate_table_html(table_id: str, df: pd.DataFrame) -> str:
    rows_html = ""
    for _, row in df.iterrows():
        rang = int(row["_rang"])
        nom = row["_nom"]
        prenom = row["_prenom"]
        pts = int(row[COL_POINTS])
        rows_html += (
            f"<tr><td class='text-center'>{rang}</td><td>{nom}</td><td>{prenom}</td>"
            f"<td class='text-end'>{pts}</td></tr>"
        )
    return (
        f'<table class="table category-points-table" id="{table_id}">'
        "<thead><tr>"
        "<th class='text-center'>Rang</th>"
        "<th>Nom</th>"
        "<th>Prénom</th>"
        "<th class='text-end'>Total points</th>"
        "</tr></thead><tbody>"
        f"{rows_html}</tbody></table>"
    )


def _generate_tabs_html(categories: list[tuple[str, str, pd.DataFrame]]) -> str:
    if not categories:
        return """<div class="alert alert-info" role="alert">
<i class="fas fa-info-circle"></i> Aucune donnée de classement n'est disponible pour le moment.
</div>"""

    nav_items = []
    panes = []
    for i, (slug, label, df) in enumerate(categories):
        active = " active" if i == 0 else ""
        show = " show" if i == 0 else ""
        table_id = f"categoryPointsTable-{slug}"
        nav_items.append(
            f'<li class="nav-item" role="presentation">'
            f'<button class="nav-link{active}" id="tab-{slug}" '
            'data-bs-toggle="tab" '
            f'data-bs-target="#pane-{slug}" type="button" role="tab" '
            f'aria-controls="pane-{slug}" aria-selected="{"true" if i == 0 else "false"}">'
            f"{label}</button></li>"
        )
        panes.append(
            f'<div class="tab-pane fade{show}{active}" id="pane-{slug}" '
            f'role="tabpanel" aria-labelledby="tab-{slug}" tabindex="0">'
            f"{_generate_table_html(table_id, df)}</div>"
        )

    return (
        '<div class="category-points-panel">'
        '<div class="category-points-tabs-toolbar">'
        '<ul class="nav category-points-tabs-nav" id="categoryPointsTabs" role="tablist">'
        + "".join(nav_items)
        + "</ul></div>"
        '<div class="tab-content category-points-tab-panels" id="categoryPointsTabContent">'
        + "".join(panes)
        + "</div></div>"
    )


def generate_markdown_webpage(filename: str, service_account_info: dict) -> None:
    file_handle = _download_spreadsheet_excel(service_account_info)

    categories: list[tuple[str, str, pd.DataFrame]] = []
    for sheet_name in SHEET_NAMES:
        df_raw = _read_category_sheet(file_handle, sheet_name)
        df_cat = _prepare_category_df(df_raw) if df_raw is not None else None
        if df_cat is not None and not df_cat.empty:
            slug = _tab_slug(sheet_name)
            label = _tab_label(sheet_name)
            categories.append((slug, label, df_cat))

    search_block = """<div class="category-points-search mb-0">
    <div class="row">
        <div class="col-md-8">
            <input type="text"
                class="form-control"
                id="categoryPointsSearch"
                placeholder="Rechercher un coureur..."
                aria-label="Rechercher un coureur">
        </div>
    </div>
</div>"""

    body = search_block + _generate_tabs_html(categories)

    with open(filename, "w") as f:
        metadata = """---
title: Classements des points par catégories
url: category_points/index.html
save_as: category_points/index.html
template: page
---
"""
        title = (
            '## <i class="fas fa-sort-amount-down fas-title"></i> '
            "Classements des points par catégories\n\n"
            '<div class="h2-spacer"></div>\n\n'
        )
        f.write(metadata + title + body)


class MissingServiceAccount(Warning):
    pass


if __name__ == "__main__":
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
    if not service_account_json:
        warnings.warn(
            "GOOGLE_SERVICE_ACCOUNT environment variable not found.",
            MissingServiceAccount,
        )
    else:
        service_account_info = json.loads(service_account_json)
        generate_markdown_webpage(
            "content/pages/category_points.md", service_account_info
        )
