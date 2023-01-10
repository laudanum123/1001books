# Tests the importer class

from io import BytesIO
import unittest.mock as mock

import pandas as pd
import pytest
import yaml

from src.importer import Importer


def test_importer_init():
    # Test the init function
    test_importer = Importer()

    assert test_importer is not None


def test_importer_import_original_list():
    # Define df as tsv replacement
    mock_tsv = pd.DataFrame({"foo_id": [1, 2, 3], "bar_id": [4, 5, 6]})

    # Create in memory BytesIO file_
    output = BytesIO()
    mock_tsv.to_csv(output, sep="\t")
    output.seek(0)  # Reset the pointer to the beginning of the file

    return_df = pd.read_csv(output, sep="\t")
    return_df = return_df.drop("Unnamed: 0", axis=1)
    print(mock_tsv)
    print(return_df)

    with mock.patch("pandas.read_csv", return_value=return_df):
        test_importer = Importer()
        test_importer.import_original_list()
        # open_mock.assert_called_once_with('source.tsv', sep='\t')

    assert mock_tsv.equals(test_importer.data)


def test_importer_reduce_to_relevant_columns():
    # Test the reduce_to_relevant_columns function
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    test_importer.reduce_to_relevant_columns(relevant_columns=["foo", "bar"])
    assert test_importer.data.columns.equals(pd.Index(["foo", "bar"]))


@mock.patch("builtins.open", mock.mock_open(read_data="data"))
@mock.patch(
    "yaml.safe_load",
    return_value=dict(
        {
            "columns": ["foo", "bar", "baz"],
            "import_file": "list.tsv",
            "database": "test.db",
        }
    ),
)
def test_read_config_file(mock_yaml):
    test_importer = Importer()
    test_importer.read_config_file("path/to/config/file")
    assert mock_yaml.called
    assert test_importer.config == dict(
        {
            "columns": ["foo", "bar", "baz"],
            "import_file": "list.tsv",
            "database": "test.db",
        }
    )


@mock.patch("builtins.open", mock.mock_open(read_data="data"))
def test_read_config_file_yaml_error():
    # Test the read_config_file function with a yaml error
    test_importer = Importer()
    with mock.patch("yaml.safe_load", side_effect=yaml.YAMLError) as exc_info:
        return_value = test_importer.read_config_file("path/to/config/file")
        assert exc_info.called
        assert return_value is False


@mock.patch("pandas.DataFrame.to_sql")
def test_write_to_sqlite(mock_to_sql):
    # Test the write_to_sqlite function
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    test_importer.write_to_sqlite("test.db")
    assert mock_to_sql.called_once()


def test_convert_column_dtypes():
    # Test the convert_column_dtypes function
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    result = test_importer.convert_column_dtypes(
        column_dtypes={"foo": "int", "bar": "str", "baz": "float"}
    )
    assert result.dtypes.equals(
        pd.Series({"foo": "int64", "bar": "object", "baz": "float64"})
    )


def test_convert_column_dtypes_with_dates():
    # Test the convert_column_dtypes function with dates as input columns
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    result = test_importer.convert_column_dtypes(
        column_dtypes={"foo": "date", "bar": "datetime64", "baz": "float"}
    )
    assert result.dtypes.equals(
        pd.Series({"foo": "datetime64[ns]", "bar": "datetime64[ns]", "baz": "float64"})
    )


def test_convert_column_dtypes_non_existing_column():
    # Test the convert_column_dtypes function with a non existing column
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    with pytest.raises(Exception):
        test_importer.convert_column_dtypes(
            column_dtypes={"foo": "int", "bar": "str", "baz": "float", "qux": "int"}
        )
        assert False

def test_convert_column_dtypes_wrong_date_format():
    # Test the convert_column_dtypes function with a wrong date format
    test_importer = Importer()
    test_importer.data = pd.DataFrame({"foo": ["thisisnotadate"]})
    with mock.patch.object(Importer, 'convert_dates_to_correct_format'):
        with pytest.raises(ValueError):
            test_importer.convert_column_dtypes(
                column_dtypes={"foo": "date"}
            )
            assert False

def test_convert_dates_to_correct_format():
    # Test the convert_columns_to_correct_format function
    test_importer = Importer()
    test_importer.data = pd.DataFrame({"foo": ["2022-12-01"]})
    test_importer.convert_dates_to_correct_format("foo")
    assert test_importer.data.dtypes.equals(pd.Series({"foo": "datetime64[ns]"}))

def test_convert_dates_to_correct_format_with_wrong_format():
    # Test the convert_columns_to_correct_format function with a wrong format
    test_importer = Importer()
    test_importer.data = pd.DataFrame({"foo": ["thisisnotadate"]})
    with mock.patch('pandas.DataFrame.apply', side_effect=pd.errors.ParserError):
        test_importer.convert_dates_to_correct_format("foo") == False
