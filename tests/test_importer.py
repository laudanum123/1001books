# Tests the importer class

import unittest.mock as mock
import pandas as pd
from io import BytesIO
from src.importer import Importer


@mock.patch.object(Importer, "read_config_file", return_value=dict({"test": "test"}))
def test_importer_init(mock_read_config_file):
    # Test the init function
    test_importer = Importer()

    assert mock_read_config_file.called
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


@mock.patch("pandas.DataFrame.to_sql")
def test_write_to_sqlite(mock_to_sql):
    # Test the write_to_sqlite function
    test_importer = Importer()
    test_importer.data = pd.DataFrame(columns=["foo", "bar", "baz"])
    test_importer.write_to_sqlite()
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
