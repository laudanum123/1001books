# Imports the data from the csv file into the database
import pandas as pd
import yaml
import sqlite3
from dateutil.parser import parse


class Importer:
    def __init__(self):
        self.config = None
        self.data = None

    def read_config_file(self, config_file: yaml) -> dict:
        # read yaml config file
        with open(config_file, "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return False
        return self.config

    def import_original_list(self) -> pd.DataFrame:
        self.data = pd.read_csv("list.tsv", sep="\t")
        return self.data

    def reduce_to_relevant_columns(self, relevant_columns: list) -> pd.DataFrame:
        self.data = self.data[relevant_columns]
        return self.data

    def write_to_sqlite(self, db_name: str) -> None:
        self.data.to_sql("books", con=sqlite3.connect(db_name), if_exists="replace")
        return self.data

    def convert_column_dtypes(self, column_dtypes: dict) -> pd.DataFrame:
        """Converts the dtypes of the columns in the dataframe to the specified dtypes"""
        # Todo: Check and convert other dtypes than datetime64

        # Check if the columns are in the dataframe
        for column in column_dtypes.keys():
            if column not in self.data.columns:
                raise Exception(f"Column {column} not in dataframe")

        # Check if date columns are in the correct format
        for column_dtype in column_dtypes.items():
            if column_dtype[1] in (
                "datetime64",
                "date",
                "time",
                "datetime",
                "timedelta",
            ):
                column_dtypes[
                    column_dtype[0]
                ] = "datetime64"  # Make sure the desired dtype is datetime64
                try:
                    pd.to_datetime(self.data[column_dtype[0]])
                except ValueError:
                    print(f"Column {column} is not in the correct format")
                    print(
                        "Trying to convert to datetime64 compatible format automatically"
                    )
                    self.data[column_dtype[0]] = self.convert_dates_to_correct_format(
                        column_dtype[0]
                    )

        # Convert the dtypes to the specified dtypes
        self.data = self.data.astype(column_dtypes)
        return self.data

    def convert_dates_to_correct_format(self, column: str) -> pd.Series:
        """Converts the dates in the column to the correct format"""
        try:
            self.data[column]= self.data.apply(lambda x: parse(x[column], fuzzy=True), axis=1)
        except pd.errors.ParserError:
            f"Could not convert {column} to datetime64 compatible format"
            return False
        return self.data[column]
