from PyQt5 import QtWidgets
from src.model import Model
from dateutil.parser import parse


class UI:

    def __init__(self, config: str):
        self.model = Model(config)
        self.model.read_data_from_db()

        self.app = QtWidgets.QApplication([])
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("Book Reading App")

        self.create_menu()

    def create_menu(self):
        # Create main menu widget
        self.menu_widget = QtWidgets.QWidget()
        self.menu_layout = QtWidgets.QVBoxLayout()
        self.menu_widget.setLayout(self.menu_layout)

        # Create buttons for menu options
        self.all_books_button = QtWidgets.QPushButton("Show all books")
        self.all_books_button.clicked.connect(self.show_all_books)
        self.menu_layout.addWidget(self.all_books_button)

        self.books_by_author_button = QtWidgets.QPushButton(
            "Show books by author")
        self.books_by_author_button.clicked.connect(self.show_books_by_author)
        self.menu_layout.addWidget(self.books_by_author_button)

        self.books_by_title_button = QtWidgets.QPushButton(
            "Show books by title")
        self.books_by_title_button.clicked.connect(self.show_books_by_title)
        self.menu_layout.addWidget(self.books_by_title_button)

        self.books_by_id_button = QtWidgets.QPushButton("Show books by id")
        self.books_by_id_button.clicked.connect(self.show_books_by_id)
        self.menu_layout.addWidget(self.books_by_id_button)

        self.edit_book_button = QtWidgets.QPushButton("Edit book details")
        self.edit_book_button.clicked.connect(self.edit_book_details)
        self.menu_layout.addWidget(self.edit_book_button)

        self.reading_progress_button = QtWidgets.QPushButton(
            "Show reading progress")
        self.reading_progress_button.clicked.connect(
            self.show_average_reading_speed)
        self.menu_layout.addWidget(self.reading_progress_button)

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.save_and_exit)
        self.menu_layout.addWidget(self.exit_button)

        self.window.setCentralWidget(self.menu_widget)
        self.window.show()
        self.app.exec_()

    def show_all_books(self):
        self.books_widget = QtWidgets.QTableWidget()
        self.books_widget.setRowCount(len(self.model.data))
        self.books_widget.setColumnCount(len(self.model.data.columns))
        self.books_widget.setHorizontalHeaderLabels(self.model.data.columns)

        for i, row in enumerate(self.model.data.values):
            for j, value in enumerate(row):
                self.books_widget.setItem(
                    i, j, QtWidgets.QTableWidgetItem(str(value)))

        self.books_widget.show()

    def show_books_by_author(self):
        author, ok = QtWidgets.QInputDialog.getText(self.window, "Author",
                                                    "Enter author: ")
        if ok:
            found_books = self.model.data[
                self.model.data["Author"].str.contains(author, case=False)]
            self.show_books(found_books)

    def show_books_by_title(self):
        title, ok = QtWidgets.QInputDialog.getText(self.window, "Title",
                                                   "Enter title: ")
        if ok:
            found_books = self.model.data[
                self.model.data["Title"].str.contains(title, case=False)]
            self.show_books(found_books)

    def show_books_by_id(self):
        book_id, ok = QtWidgets.QInputDialog.getText(self.window, "Book ID",
                                                     "Enter book id: ")
        if ok:
            found_books = self.model.data[self.model.data["index"] == int(
                book_id)]
            self.show_books(found_books)

    def show_books(self, found_books):
        self.books_widget = QtWidgets.QTableWidget()
        self.books_widget.setRowCount(len(found_books))
        self.books_widget.setColumnCount(len(found_books.columns))
        self.books_widget.setHorizontalHeaderLabels(found_books.columns)

        for i, row in enumerate(found_books.values):
            for j, value in enumerate(row):
                self.books_widget.setItem(
                    i, j, QtWidgets.QTableWidgetItem(str(value)))

        self.books_widget.show()

    def edit_book_details(self):
        book_id, ok = QtWidgets.QInputDialog.getText(self.window, "Book ID",
                                                     "Enter book id: ")
        if ok:
            found_books = self.model.data[self.model.data["index"] == int(
                book_id)]
            self.show_books(found_books)

            # Get new values for start/finish dates from user
            start_new_value, ok = QtWidgets.QInputDialog.getText(
                self.window, "Start Date",
                "Enter start reading date (YYYY-MM-DD): ")
            if ok:
                finish_new_value, ok = QtWidgets.QInputDialog.getText(
                    self.window, "Finish Date",
                    "Enter finish reading date (YYYY-MM-DD): ")
                if ok:
                    try:
                        start_date = parse(start_new_value)
                        finish_date = parse(finish_new_value)
                        self.model.data.loc[self.model.data["index"] ==
                                            int(book_id), "Date Started"] = start_date
                        self.model.data.loc[self.model.data["index"] ==
                                            int(book_id),
                                            "Date Finished"] = finish_date
                        self.show_books(found_books)
                    except ValueError:
                        QtWidgets.QMessageBox.warning(
                            self.window, "Error",
                            "Invalid date format. Please enter dates in the format YYYY-MM-DD."
                        )

    def show_average_reading_speed(self):
        reading_speed = self.model.calculate_average_reading_speed()
        QtWidgets.QMessageBox.information(
            self.window, "Reading Speed",
            f"Your average reading speed is {reading_speed} pages per day.")

    def save_and_exit(self):
        self.model.write_to_sqlite(write_index=False)
        self.app.exit()
