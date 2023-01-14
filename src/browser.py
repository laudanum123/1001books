import sqlite3
import datetime
import pandas as pd
from tabulate import tabulate
from dateutil.parser import parse
from src.model import Model


class Browser:
    def __init__(self, config: str):
        self.model = Model(config)
        self.model.read_data_from_db()

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
            self.show_reading_progress()
        elif choice == "q":
            self.save_and_exit()
            return
        else:
            print("Invalid choice")
        self.menu()

    def show_all_books(self):
        for row_number in range(51, len(self.model.data) + 51, 51):
            print(
                tabulate(
                    self.model.data[row_number - 50 : row_number],
                    headers="keys",
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
            input("Press enter to continue")

    # TODO: Refactor this to select books by criteria in single function
    def show_books_by_author(self) -> pd.DataFrame:
        author = input("Enter author: ")
        found_books = self.model.data[
            self.model.data["Author"].str.contains(author, case=False)
        ]
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
        found_books = self.model.data[
            self.model.data["Title"].str.contains(title, case=False)
        ]
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
        found_books = self.model.data[self.model.data["index"] == int(book_id)]
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
        found_books = self.model.data[self.model.data["index"] == int(book_id)]
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
        self.model.data.loc[
            self.model.data["index"] == int(book_id), "Date Started"
        ] = pd.to_datetime(parse(start_new_value, fuzzy=True))
        end_new_value = input("Enter end reading date (YYYY-MM-DD): ")
        self.model.data.loc[
            self.model.data["index"] == int(book_id), "Date Finished"
        ] = pd.to_datetime(parse(end_new_value, fuzzy=True))
        print(
            tabulate(
                self.model.data[self.model.data["index"] == int(book_id)],
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return self.model.data[self.model.data["index"] == int(book_id)]

    def save_and_exit(self):
        want_to_save = input("Do you want to save changes? (y/n): ")
        if want_to_save == "y":
            try:
                self.update_kpi()
                self.model.write_to_sqlite()
                print("Changes saved")
            except Exception as e:
                print(e)
                return False
        else:
            print("Changes not saved")

    def update_kpi(self):
        self.model.data["Days Read"] = (
            self.model.data["Date Finished"] - self.model.data["Date Started"]
        ).dt.days
        self.model.data["Pages per Day"] = (
            self.model.data["Pages"] / self.model.data["Days Read"]
        )

    def show_reading_progress(self):
        # Get the current date
        today = datetime.datetime.now().date()

        # Find the books that have not been finished yet
        unfinished_books = self.model.data[self.model.data["Date Finished"].isna()]

        # Find the total number of pages in unfinished books
        total_pages = unfinished_books["Pages"].sum()

        # Find the number of pages the user has read so far
        finished_books = self.model.data[self.model.data["Date Finished"].notna()]
        pages_read = finished_books["Pages"].sum()

        # Find the number of pages the user needs to read
        pages_to_read = total_pages - pages_read

        # Find the number of days the user has been reading
        days_reading = (today - min(self.model.data["Date Started"])).days

        # Find the number of days the user needs to read to finish all books
        days_to_finish = pages_to_read * days_reading / pages_read

        # Calculate the age the user will be when they finish reading all the books
        start_date = min(self.model.data["Date Started"])
        age_when_finish = (
            start_date + datetime.timedelta(days=days_to_finish)
        ).year - today.year

        print(
            f"You will be {age_when_finish} years old when you finish reading all the books on the list."
        )
