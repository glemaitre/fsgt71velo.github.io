import pandas as pd

from ..generate_calendar import (
    COLOR_CIRCUIT_LENGTH,
    COLOR_DURATION_RACE,
    COLOR_TYPE_OF_RACE,
    SHEET_CALENDAR,
    SHEET_ID,
    URL_CALENDAR,
    generate_html_table,
)


def test_calendar_google_sheet():
    """Check that the id, sheet, and URL are correct."""
    assert SHEET_ID == "1Nrau-4Qwbp91pQ8fSi7HCf-OsL67-b2JcKIvnimh2F8"
    assert SHEET_CALENDAR == "calendar"
    assert URL_CALENDAR == (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
        f"tq?tqx=out:csv&sheet={SHEET_CALENDAR}"
    )


def test_calendar_dataframe():
    """Check that the loaded dataframe contains the expected information to build the
    HTML page.
    """
    df_calendar = pd.read_csv(URL_CALENDAR, dayfirst=True, parse_dates=["Date"])

    expected_columns = [
        "Date",
        "Durée organisation",
        "Course",
        "Type de course",
        "Longeur circuit",
        "Catégories",
        "Club",
        "Affiche",
        "Résultats TC",
        "Résultats école",
    ]
    for col in expected_columns:
        assert (
            col in df_calendar.columns
        ), f"Column {col} is missing in the calendar dataframe"

    assert pd.api.types.is_datetime64_any_dtype(
        df_calendar["Date"]
    ), "The 'Date' column should be a datetime object"

    expected_duration = list(COLOR_DURATION_RACE.keys())
    for duration in df_calendar["Durée organisation"].unique():
        if pd.isna(duration):
            # we accept empty duration
            continue
        assert (
            duration in expected_duration
        ), f"Unexpected duration: {duration}. Should be one of {expected_duration}"

    expected_type_of_race = list(COLOR_TYPE_OF_RACE.keys())
    for type_of_race in df_calendar["Type de course"].unique():
        assert type_of_race in expected_type_of_race, (
            f"Unexpected type of race: {type_of_race}. Should be one of "
            f"{expected_type_of_race}"
        )

    expected_circuit_length = list(COLOR_CIRCUIT_LENGTH.keys())
    for circuit_length in df_calendar["Longeur circuit"].unique():
        if pd.isna(circuit_length):
            # we accept empty circuit length
            continue
        assert circuit_length in expected_circuit_length, (
            f"Unexpected circuit length: {circuit_length}. Should be one of "
            f"{expected_circuit_length}"
        )


def test_generate_html_table():
    """Check that we generate a sensible HTML table."""
    df_calendar = pd.read_csv(URL_CALENDAR, dayfirst=True, parse_dates=["Date"])
    html_table = generate_html_table(df_calendar)

    # check the header
    header = (
        '<table class="table" id="calendarTable"><thead><tr>'
        '<th class="text-center">Dates</th>'
        '<th class="text-center">Courses</th>'
        '<th class="text-center">Catégories</th>'
        '<th class="text-center">Club</th>'
        "</tr></thead>"
        "<tbody>"
    )
    assert html_table.startswith(header)
    end_table = "</tbody></table>"
    assert html_table.endswith(end_table)


def test_generate_html_table_includes_year_in_headers_and_dates():
    """Check that section headers and date cells include the year (for calendars
    spanning two years)."""
    df = pd.DataFrame(
        [
            {
                "Date": pd.Timestamp("2026-03-15"),
                "Durée organisation": "Demi-journée",
                "Course": "Course test 2026",
                "Type de course": "Route",
                "Longeur circuit": "Circuit >= 5 km",
                "Catégories": "Masters",
                "Club": "Club A",
                "Affiche": pd.NA,
                "Résultats TC": pd.NA,
                "Résultats école": pd.NA,
                "Annulé": pd.NA,
            },
            {
                "Date": pd.Timestamp("2027-01-10"),
                "Durée organisation": "Journée complète",
                "Course": "Course test 2027",
                "Type de course": "Contre-la-montre",
                "Longeur circuit": "Circuit < 5km",
                "Catégories": "Tous",
                "Club": "Club B",
                "Affiche": pd.NA,
                "Résultats TC": pd.NA,
                "Résultats école": pd.NA,
                "Annulé": pd.NA,
            },
        ]
    )
    html_table = generate_html_table(df)

    # Section headers must include year (e.g. "MARS 2026", "JANVIER 2027")
    assert "MARS 2026" in html_table
    assert "JANVIER 2027" in html_table

    # Date cells must include year (e.g. "Mar 15 Mar 2026")
    assert "2026" in html_table
    assert "2027" in html_table

    # Section headers must appear in chronological order (month order: Jan, Feb, ... Dec)
    # Use data in "wrong" order: Jan 2027 then Dec 2026; output must be Dec 2026 then Jan 2027
    df_reversed = pd.DataFrame(
        [
            {
                "Date": pd.Timestamp("2027-01-10"),
                "Durée organisation": "Demi-journée",
                "Course": "Course 2027",
                "Type de course": "Route",
                "Longeur circuit": "Circuit >= 5 km",
                "Catégories": "Tous",
                "Club": "Club B",
                "Affiche": pd.NA,
                "Résultats TC": pd.NA,
                "Résultats école": pd.NA,
                "Annulé": pd.NA,
            },
            {
                "Date": pd.Timestamp("2026-12-05"),
                "Durée organisation": "Journée complète",
                "Course": "Course 2026",
                "Type de course": "Contre-la-montre",
                "Longeur circuit": "Circuit < 5km",
                "Catégories": "Masters",
                "Club": "Club A",
                "Affiche": pd.NA,
                "Résultats TC": pd.NA,
                "Résultats école": pd.NA,
                "Annulé": pd.NA,
            },
        ]
    )
    html_reversed = generate_html_table(df_reversed)
    # DECEMBRE 2026 must appear before JANVIER 2027
    pos_dec_2026 = html_reversed.find("DÉCEMBRE 2026")
    pos_jan_2027 = html_reversed.find("JANVIER 2027")
    assert pos_dec_2026 != -1 and pos_jan_2027 != -1 and pos_dec_2026 < pos_jan_2027
