from ..generate_report import (
    format_date_from_filename,
)


def test_format_date_from_filename():
    """Check that we properly format the date from the filename."""
    assert format_date_from_filename("01_01_2024.pdf") == "1 Janvier 2024"
    assert format_date_from_filename("01_02_2024.pdf") == "1 Février 2024"
