from src.importer import Importer

# Features:
# - Import data from tsv file
# - Reduce to relevant columns
# - Calculate days read and pages per day
# - Save to database
# - Display current progress in overall reading progress (e.g. 10% of books read)
# - Display age when list finished at current reading speed


if __name__ == "__main__":
    importer = Importer()
    importer.read_config_file("config/config.yaml")
    importer.import_original_list()
    importer.reduce_to_relevant_columns(relevant_columns=importer.config["relevant_columns"])
    importer.write_to_sqlite()
    print(importer.data)
