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
    assert SHEET_ID == "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M"
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
    assert df_calendar["Date"].dt.year.unique() == [2025], "The year should be 2025"

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
        '<table class="table" id="calendarTable">'
        "<thead><tr>"
        "<th>Dates</th>"
        "<th>Courses</th>"
        "<th>Catégories</th>"
        "<th>Club</th>"
        "</tr></thead>"
        "<tbody>"
    )
    assert html_table.startswith(header)
    end_table = "</tbody></table>"
    assert html_table.endswith(end_table)
