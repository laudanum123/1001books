import sqlite3
import pandas as pd
from tabulate import tabulate
from dateutil.parser import parse


class Browser:
    def __init__(self, db_name: str):
        self.data = pd.read_sql("select * from books", con=sqlite3.connect(db_name))
        self.data = self.data.replace("\\n", " ")

    def menu(self):
        print("Menu")
        print("1. Show all books")
        print("2. Show books by author")
        print("3. Show books by title")
        print("4. Show books by id")
        print("5. Edit book details")
        print("q to exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            self.show_all_books()
        elif choice == "2":
            self.show_books_by_author()
        elif choice == "3":
            self.show_books_by_title()
        elif choice == "4":
            self.show_books_by_id()
        elif choice == "5":
            self.edit_book_details()
        elif choice == "q":
            return
        else:
            print("Invalid choice")
        self.menu()

    def show_all_books(self):
        for row_number in range(51, len(self.data) + 51, 51):
            print(
                tabulate(
                    self.data[row_number - 50 : row_number],
                    headers="keys",
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
            input("Press enter to continue")

    # TODO: Refactor this to select books by criteria in single function
    def show_books_by_author(self) -> pd.DataFrame:
        author = input("Enter author: ")
        found_books = self.data[self.data["Author"].str.contains(author, case=False)]
        print(
            tabulate(
                found_books,
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return found_books

    def show_books_by_title(self) -> pd.DataFrame:
        title = input("Enter title: ")
        found_books = self.data[self.data["Title"].str.contains(title, case=False)]
        print(
            tabulate(
                found_books,
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return found_books

    def show_books_by_id(self) -> pd.DataFrame:
        book_id = input("Enter book id: ")
        found_books = self.data[self.data["index"] == int(book_id)]
        print(
            tabulate(
                found_books,
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return found_books

    def edit_book_details(self):
        book_id = input("Enter book id: ")
        found_books = self.data[self.data["index"] == int(book_id)]
        print(
            tabulate(
                found_books,
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        # Get new values for start/finish dates from user
        start_new_value = input("Enter start reading date (YYYY-MM-DD): ")
        self.data.loc[
            self.data["index"] == int(book_id), "Date Started"
        ] = pd.to_datetime(parse(start_new_value, fuzzy=True))
        end_new_value = input("Enter end reading date (YYYY-MM-DD): ")
        self.data.loc[
            self.data["index"] == int(book_id), "Date Finished"
        ] = pd.to_datetime(parse(end_new_value, fuzzy=True))
        print(
            tabulate(
                self.data[self.data["index"] == int(book_id)],
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return self.data[self.data["index"] == int(book_id)]
