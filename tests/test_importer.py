# Tests the importer class

from io import BytesIO
from src.model import Model
import unittest.mock as mock

import pandas as pd
import pytest
import yaml

from src.browser import Browser
from src.importer import Importer


def importer():
    with mock.patch.object(Model, "__init__", return_value=None):
        importer = Importer("path/to/config")
        importer.model = mock.create_autospec(Model)
        return importer


test_importer = importer()


def test_importer_init():
    # Test the init function
    with mock.patch.object(Model, "__init__", return_value=None) as mock_init:
        test_importer = Importer("/path/to/config")

        assert mock_init.called
        assert test_importer is not None


def test_importer_reduce_to_relevant_columns():
    # Test the reduce_to_relevant_columns function
    test_importer.model.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    test_importer.model.data = test_importer.reduce_to_relevant_columns(
        relevant_columns=["foo", "bar"]
    )
    assert test_importer.model.data.columns.equals(pd.Index(["foo", "bar"]))


def test_convert_column_dtypes():
    # Test the convert_column_dtypes function
    test_importer.model.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    result = test_importer.convert_column_dtypes(
        column_dtypes={"foo": "int", "bar": "str", "baz": "float"}
    )
    assert result.dtypes.equals(
        pd.Series({"foo": "int64", "bar": "object", "baz": "float64"})
    )


def test_convert_column_dtypes_with_dates():
    # Test the convert_column_dtypes function with dates as input columns
    test_importer.model.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    result = test_importer.convert_column_dtypes(
        column_dtypes={"foo": "date", "bar": "datetime64", "baz": "float"}
    )
    assert result.dtypes.equals(
        pd.Series({"foo": "datetime64[ns]", "bar": "datetime64[ns]", "baz": "float64"})
    )


def test_convert_column_dtypes_non_existing_column():
    # Test the convert_column_dtypes function with a non existing column
    test_importer.model.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    with pytest.raises(Exception):
        test_importer.convert_column_dtypes(
            column_dtypes={"foo": "int", "bar": "str", "baz": "float", "qux": "int"}
        )
        assert False


def test_convert_column_dtypes_wrong_date_format():
    # Test the convert_column_dtypes function with a wrong date format
    test_importer.model.data = pd.DataFrame({"foo": ["thisisnotadate"]})
    with mock.patch.object(Importer, "convert_dates_to_correct_format"):
        with pytest.raises(ValueError):
            test_importer.convert_column_dtypes(column_dtypes={"foo": "date"})
            assert False


def test_convert_dates_to_correct_format():
    # Test the convert_columns_to_correct_format function
    test_importer.model.data = pd.DataFrame({"foo": ["2022-12-01"]})
    test_importer.convert_dates_to_correct_format("foo")
    assert test_importer.model.data.dtypes.equals(pd.Series({"foo": "datetime64[ns]"}))


def test_convert_dates_to_correct_format_with_wrong_format():
    # Test the convert_columns_to_correct_format function with a wrong format
    test_importer.model.data = pd.DataFrame({"foo": ["thisisnotadate"]})
    with mock.patch("pandas.DataFrame.apply", side_effect=pd.errors.ParserError):
        assert test_importer.convert_dates_to_correct_format("foo") == False
