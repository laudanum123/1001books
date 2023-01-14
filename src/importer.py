# Imports the data from the csv file into the database
import pandas as pd
from dateutil.parser import parse
from src.model import Model


class Importer:
    def __init__(self, config_file: str):
        self.model = Model(config_file)

    def perform_import(self):
        self.model.import_original_list("list.tsv")
        self.model.data = self.reduce_to_relevant_columns(
            self.model.config["relevant_columns"]
        )
        self.model.data = self.convert_column_dtypes(self.model.config["column_dtypes"])
        self.model.data = self.model.write_to_sqlite()

    def reduce_to_relevant_columns(self, relevant_columns: list) -> pd.DataFrame:
        reduced_dataframe = self.model.data[relevant_columns]
        return reduced_dataframe

    def convert_column_dtypes(self, column_dtypes: dict) -> pd.DataFrame:
        """Converts the dtypes of the columns in the dataframe to the specified dtypes"""
        # Todo: Check and convert other dtypes than datetime64

        # Check if the columns are in the dataframe
        for column in column_dtypes.keys():
            if column not in self.model.data.columns:
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
                    pd.to_datetime(self.model.data[column_dtype[0]])
                except ValueError:
                    print(f"Column {column} is not in the correct format")
                    print(
                        "Trying to convert to datetime64 compatible format automatically"
                    )
                    self.model.data[
                        column_dtype[0]
                    ] = self.convert_dates_to_correct_format(column_dtype[0])

        # Convert the dtypes to the specified dtypes
        self.model.data = self.model.data.astype(column_dtypes)
        return self.model.data

    def convert_dates_to_correct_format(self, column: str) -> pd.Series:
        """Converts the dates in the column to the correct format"""
        try:
            self.model.data[column] = self.model.data.apply(
                lambda x: parse(x[column], fuzzy=True), axis=1
            )
        except pd.errors.ParserError:
            f"Could not convert {column} to datetime64 compatible format"
            return False
        return self.model.data[column]
