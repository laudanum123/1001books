from src.model import Model
from unittest import mock
import yaml
import pandas as pd
import sqlite3
import os


def test_init():
    with mock.patch.object(Model, "read_config_file") as mock_read_config_file:
        mock_read_config_file.return_value = {"foo": "bar"}
        model = Model("path/to/config.json")
        assert model.config == {"foo": "bar"}


def test_read_data_from_db():
    with mock.patch.object(Model, "read_config_file") as mock_read_config_file:
        mock_read_config_file.return_value = {"db_name": "bar"}
        model = Model("path/to/config.json")
        with mock.patch(
            "pandas.read_sql",
            return_value={"column_dtypes": {"foo": "date", "bar": "int"}},
        ) as mock_read_data_from_db:
            with mock.patch.object(
                Model, "convert_columns_to_datetime", return_value="baz"
            ) as mock_convert_columns_to_datetime:
                model.read_data_from_db()
                assert model.data == "baz"


@mock.patch("builtins.open", mock.mock_open(read_data="data"))
def test_read_config_file_yaml_error():
    # Test the read_config_file function with a yaml error
    with mock.patch("yaml.safe_load", side_effect=yaml.YAMLError) as exc_info:
        model = Model("path/to/config.json")
        return_value = model.read_config_file("path/to/config/file")
        assert exc_info.called
        assert return_value is False


def test_convert_columns_to_datetime():
    # Create a test DataFrame with date columns
    test_data = {
        "date1": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "date2": ["2022-01-04", "2022-01-05", "2022-01-06"],
        "other": [1, 2, 3],
    }
    df = pd.DataFrame(test_data)

    # Create an instance of the class
    with mock.patch.object(Model, "read_config_file") as mock_read_config_file:
        mock_read_config_file.return_value = {"db_name": "bar"}
        model = Model("path/to/config.json")
    model.data = df
    # Convert date columns to datetime
    model.convert_columns_to_datetime(["date1", "date2"])

    # Assert that the columns have been converted to datetime
    assert model.data["date1"].dtype == "datetime64[ns]"
    assert model.data["date2"].dtype == "datetime64[ns]"

    # Assert that other columns have not been affected
    assert model.data["other"].dtype != "datetime64[ns]"


def test_write_to_sqlite():
    # Create a test DataFrame
    test_data = {
        "title": ["Book 1", "Book 2", "Book 3"],
        "author": ["Author 1", "Author 2", "Author 3"],
        "year": [2000, 2001, 2002],
    }
    df = pd.DataFrame(test_data)

    with mock.patch.object(Model, "read_config_file") as mock_read_config_file:
        mock_read_config_file.return_value = {"db_name": "bar"}
        model = Model("path/to/config.json")

    model.data = df

    # Set the database name
    model.db_name = "test.db"

    # write to sqlite
    model.write_to_sqlite()

    # Connect to the database
    con = sqlite3.connect("test.db")

    # Read the data from the database
    read_data = pd.read_sql_query("SELECT * from books", con)

    # Assert that the data in the DataFrame is same as the data in the database
    pd.testing.assert_frame_equal(df, read_data[["title", "author", "year"]])

    # test for no index
    model.write_to_sqlite(write_index=False)
    read_data = pd.read_sql_query("SELECT * from books", con)
    assert read_data.index.name != "index"

    # Close the connection
    con.close()

    # Clean up the test database
    os.remove("test.db")


def test_import_original_list():
    # Create a test DataFrame
    sample_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    # create an instance of the class that contains the import_original_list method
    # write the sample DataFrame to a file
    sample_df.to_csv("list.tsv", sep="\t", index=False)

    with mock.patch.object(Model, "read_config_file") as mock_read_config_file:
        mock_read_config_file.return_value = {"db_name": "bar"}
        model = Model("path/to/config.json")

    model.data = sample_df
    # call the import_original_list method on the test instance
    result = model.import_original_list("list.tsv")

    # assert that the returned DataFrame is equal to the sample DataFrame
    assert result.equals(sample_df)
