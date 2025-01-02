import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

from ..generate_listing_update_double_licence import (
    SPREADSHEET_ID,
    generate_listing,
)


@pytest.fixture
def service_account_info():
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
    if not service_account_json:
        pytest.skip("GOOGLE_SERVICE_ACCOUNT environment variable not found")
    return json.loads(service_account_json)


@pytest.fixture
def mock_values_empty():
    return {"values": []}


@pytest.fixture
def mock_values_header_only():
    return {
        "values": [
            [
                "Timestamp",
                "Civilité",
                "Nom",
                "Prénom",
                "Date de naissance",
                "Email",
                "Numéro de licence FSGT",
                "Catégorie FSGT 71",
                "Club FSGT",
                "Numéro de licence FFC",
                "Catégorie FFC",
                "Club FFC",
                "Message",
            ]
        ]
    }


@pytest.fixture
def mock_values_old_data():
    old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "values": [
            [
                "Timestamp",
                "Civilité",
                "Nom",
                "Prénom",
                "Date de naissance",
                "Email",
                "Numéro de licence FSGT",
                "Catégorie FSGT 71",
                "Club FSGT",
                "Numéro de licence FFC",
                "Catégorie FFC",
                "Club FFC",
                "Message",
            ],
            [
                old_date,
                "M.",
                "Doe",
                "John",
                "1990-01-01",
                "john@example.com",
                "1234567890",
                "1",
                "xxx",
                "1234567890",
                "1",
                "xxx",
                "Message",
            ],
        ]
    }


@pytest.fixture
def mock_values_mixed_data():
    recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "values": [
            [
                "Timestamp",
                "Civilité",
                "Nom",
                "Prénom",
                "Date de naissance",
                "Email",
                "Numéro de licence FSGT",
                "Catégorie FSGT 71",
                "Club FSGT",
                "Numéro de licence FFC",
                "Catégorie FFC",
                "Club FFC",
                "Message",
            ],
            [
                recent_date,
                "M.",
                "Doe",
                "John",
                "1990-01-01",
                "john@example.com",
                "1234567890",
                "1",
                "xxx",
                "1234567890",
                "1",
                "xxx",
                "Message",
            ],
            [
                recent_date,
                "Mme",
                "Smith",
                "Jane",
                "1985-05-05",
                "jane@example.com",
                "1234567890",
                "1",
                "xxx",
                "1234567890",
                "1",
                "xxx",
                "Message",
            ],
            [
                old_date,
                "M.",
                "Smith",
                "Jane",
                "1985-05-05",
                "jane@example.com",
                "1234567890",
                "1",
                "xxx",
                "1234567890",
                "1",
                "xxx",
                "Message",
            ],
        ]
    }


def test_spreadsheet_id():
    """Check that we have the expected spreadsheet id."""
    assert SPREADSHEET_ID == "1lZwxoMeF2gBuFLgjoaBREPl8YFESYwJLV5o1JEjKHKI"


@pytest.mark.parametrize(
    "mock_data, expected_file_exists, expected_rows",
    [
        ("mock_values_empty", False, 0),
        ("mock_values_header_only", False, 0),
        ("mock_values_old_data", False, 0),
        ("mock_values_mixed_data", True, 2),
    ],
)
def test_generate_listing_scenarios(
    tmp_path,
    request,
    mock_data,
    expected_file_exists,
    expected_rows,
    service_account_info,
):
    output_file = tmp_path / "test_output.csv"
    mock_data = request.getfixturevalue(mock_data)

    with patch(
        "scripts.generate_listing_update_double_licence._get_values"
    ) as mock_get_values:
        mock_get_values.return_value = mock_data["values"]

        generate_listing(str(output_file), service_account_info)

        assert output_file.exists() == expected_file_exists
        if expected_file_exists:
            df = pd.read_csv(output_file)
            assert len(df) == expected_rows
            if mock_data == mock_values_mixed_data:
                assert all(
                    pd.to_datetime(df["Timestamp"])
                    >= (datetime.now() - timedelta(days=7))
                )
