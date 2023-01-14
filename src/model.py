import pandas as pd
import sqlite3
import yaml


class Model:
    def __init__(self, config_file: yaml):
        self.data = None
        self.config = self.read_config_file(config_file)

    def read_data_from_db(self):
        self.data = pd.read_sql(
            "select * from books", con=sqlite3.connect(self.config["db_name"])
        )
        date_columns = [
            k for k, v in self.config["column_dtypes"].items() if v == "date"
        ]
        self.data = self.convert_columns_to_datetime(date_columns)

    def convert_columns_to_datetime(self, columns: list):
        for column in columns:
            self.data[column] = pd.to_datetime(self.data[column])
        return self.data

    def read_config_file(self, config_file: yaml) -> dict:
        # read yaml config file and return as dict
        with open(config_file, "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return False
        return self.config

    def import_original_list(self, list_file) -> pd.DataFrame:
        self.data = pd.read_csv(list_file, sep="\t")
        return self.data

    def write_to_sqlite(self, write_index=True) -> None:
        self.data.to_sql(
            "books",
            con=sqlite3.connect(self.config["db_name"]),
            if_exists="replace",
            index=write_index,
        )
        return self.data
