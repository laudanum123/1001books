import sqlite3
import pandas as pd
from tabulate import tabulate
from dateutil.parser import parse
from src.browser import Browser


class Browser:
    def __init__(self, db_name: str):
        self.data = pd.read_sql("select * from books", con=sqlite3.connect(db_name))
        self.db_name = db_name

    def menu(self):
        print("Menu")
        print("1. Show all books")
        print("2. Show books by author")
        print("3. Show books by title")
        print("4. Show books by id")
        print("5. Edit book details")
        print("6. Show reading progress")
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
        elif choice == "6":
            pass
        elif choice == "q":
            self.save_and_exit(self.db_name)
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

    def convert_columns_to_datetime(self, columns: list):
        for column in columns:
            self.data[column] = pd.to_datetime(self.data[column])
        return self.data

    def save_and_exit(self, db_name: str):
        want_to_save = input("Do you want to save changes? (y/n): ")
        if want_to_save == "y":
            try:
                self.update_kpi()
                self.data.to_sql(
                    "books",
                    con=sqlite3.connect(db_name),
                    if_exists="replace",
                    index=False,
                )
                print("Changes saved")
            except Exception as e:
                print(e)
                return False
        else:
            print("Changes not saved")

    def update_kpi(self):
        self.data["Days Read"] = (
            self.data["Date Finished"] - self.data["Date Started"]
        ).dt.days
        self.data["Pages per Day"] = self.data["Pages"] / self.data["Days Read"]
