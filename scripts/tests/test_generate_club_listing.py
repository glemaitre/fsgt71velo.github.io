import pandas as pd
import pytest

from ..generate_club_listing import (
    SHEET_DIRECTORY,
    SHEET_ID,
    SHEET_LISTING,
    URL_DIRECTORY,
    URL_LISTING,
    generate_club_listing,
    generate_person_dropdown,
)


@pytest.mark.parametrize(
    "sheet_id, sheet_name, url, expected_sheet_name",
    [
        (SHEET_ID, SHEET_LISTING, URL_LISTING, "Listing"),
        (SHEET_ID, SHEET_DIRECTORY, URL_DIRECTORY, "Annuaire"),
    ],
)
def test_calendar_google_sheet(sheet_id, sheet_name, url, expected_sheet_name):
    """Check that the id, sheet, and URL are correct."""
    assert sheet_id == "1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM"
    assert sheet_name == expected_sheet_name
    assert url == (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/"
        f"tq?tqx=out:csv&sheet={sheet_name}"
    )


def test_df_listing():
    """Check the integrity of the listing dataframe."""
    df_listing = pd.read_csv(URL_LISTING)

    expected_columns = (
        "Nom du club",
        "Ville",
        "Président Nom",
        "Président Prénom",
        "Responsable cyclisme Nom",
        "Responsable cyclisme Prénom",
        "Responsable cyclotouriste Nom",
        "Responsable cyclotouriste Prénom",
        "Correspondant VTT Nom",
        "Correspondant VTT Prénom",
        "Correspondant vélos enfants Nom",
        "Correspondant vélos enfants Prénom",
    )
    for column in expected_columns:
        assert column in df_listing.columns, f"Column {column} not found in df_listing"


def test_df_directory():
    """Check the integrity of the directory dataframe."""
    df_directory = pd.read_csv(URL_DIRECTORY)

    expected_columns = (
        "Prénom",
        "Nom",
        "Téléphone",
        "Mobile",
        "Email",
        "Adresse",
    )
    for column in expected_columns:
        assert (
            column in df_directory.columns
        ), f"Column {column} not found in df_directory"


def test_integrity_listing_directory():
    """Check that the different first name and last name from the listing are present
    in the directory.
    """
    df_listing = pd.read_csv(URL_LISTING)
    df_directory = pd.read_csv(URL_DIRECTORY)

    for position in [
        "Président",
        "Responsable cyclisme",
        "Responsable cyclotouriste",
        "Correspondant VTT",
        "Correspondant vélos enfants",
    ]:
        for first_name, last_name in zip(
            df_listing[f"{position} Prénom"], df_listing[f"{position} Nom"]
        ):
            if pd.isna(first_name) or pd.isna(last_name):
                continue

            matching_entries = df_directory.query(
                f"Prénom == '{first_name}' & Nom == '{last_name}'"
            )
            assert (
                len(matching_entries) > 0
            ), f"{position} {first_name} {last_name} not found in directory"


def test_generate_person_dropdown():
    """Check that we properly generate the person dropdown table."""
    df_directory = pd.read_csv(URL_DIRECTORY)
    html_table = generate_person_dropdown(
        df_directory,
        first_name="Cédric",
        last_name="LEMAITRE",
        counter_unique_dropdown=0,
    )

    table_html_cedric_lemaitre = (
        '<div class="dropdown">'
        '<button class="btn btn-link dropdown-toggle" type="button" '
        'id="contactDropdown0" data-bs-toggle="dropdown" aria-expanded="false">'
        "Cédric LEMAITRE"
        "</button>"
        '<div class="dropdown-menu p-3" aria-labelledby="contactDropdown0">'
        '<table class="contact-info-table">'
        '<tr><td><i class="fas fa-map-marker-alt"></i></td>'
        "<td>40 avenue de la libération<br>71210 MONTCHANIN</td></tr>"
        '<tr><td><i class="fas fa-mobile-alt"></i></td>'
        "<td>06.72.71.55.84</td></tr>"
        '<tr><td><i class="fas fa-envelope"></i></td>'
        '<td><a href="mailto:c.lemaitre58@gmail.com">c.lemaitre58@gmail.com</a></td>'
        "</tr>"
        "</table>"
        "</div>"
        "</div>"
    )
    assert html_table == table_html_cedric_lemaitre


def test_generate_club_listing():
    """Check that we properly generate the club listing table."""
    df_listing = pd.read_csv(URL_LISTING)
    df_directory = pd.read_csv(URL_DIRECTORY)
    html_table = generate_club_listing(df_listing, df_directory)

    # check the header
    header = (
        '<table class="table" id="clubTable"><thead><tr>'
        "<th>Club</th>"
        "<th>Contacts</th>"
        "</tr></thead>"
    )
    assert html_table.startswith(header)
    end_table = "</tbody></table>"
    assert html_table.endswith(end_table)
