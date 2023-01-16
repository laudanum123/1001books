from src.importer import Importer
from src.ui import UI
import os

# Features:
# - Display current progress in overall reading progress (e.g. 10% of books read)
# - Display age when list finished at current reading speed


if __name__ == "__main__":
    if not os.path.exists("books.db"):
        importer = Importer("config/config.yaml")
        importer.perform_import()
    ui = UI("config/config.yaml")
    ui.create_menu()
    # browser = Browser("config/config.yaml")
    # browser.menu()
