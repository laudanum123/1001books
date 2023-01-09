from src.importer import Importer
from src.browser import Browser
import os

# Features:
# - Display current progress in overall reading progress (e.g. 10% of books read)
# - Display age when list finished at current reading speed


if __name__ == "__main__":
    if not os.path.exists("test.db"):
        importer = Importer()
        importer.read_config_file("config/config.yaml")
        importer.import_original_list()
        importer.reduce_to_relevant_columns(
            relevant_columns=importer.config["relevant_columns"]
        )
        importer.convert_column_dtypes(column_dtypes=importer.config["column_dtypes"])
        importer.write_to_sqlite("test.db")

    browser = Browser(db_name="test.db")
    browser.menu()
