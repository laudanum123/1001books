from os import wait
import sqlite3
import datetime
import pandas as pd
from tabulate import tabulate
from dateutil.parser import parse
from src.model import Model
import numpy as np

pd.options.mode.chained_assignment = None


class Browser:
    def __init__(self, config: str):
        self.model = Model(config)
        self.model.read_data_from_db()

    def menu(self):
        print("\n\n\nMenu")
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
            self.show_average_reading_speed()
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
            key_press = input("Press enter to continue or q to quit: ")
            if key_press == "q":
                break

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
        if start_new_value:
            self.model.data.loc[
                self.model.data["index"] == int(book_id), "Date Started"
            ] = pd.to_datetime(parse(start_new_value, fuzzy=True))
        end_new_value = input("Enter end reading date (YYYY-MM-DD): ")
        if end_new_value:
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
                self.model.write_to_sqlite(write_index=False)
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
        # filter out books that haven't been started
        progress = self.model.data[self.model.data["Date Started"].notna()]
        progress = progress[progress["Date Finished"].notna()]
        # convert to reading days
        progress["Reading Days"] = (
            progress["Date Finished"] - progress["Date Started"]
        ).dt.days
        # replace 0 days with 1 day in order to avoid division by 0
        progress["Reading Days"] = progress["Reading Days"].replace(0, 1)
        # calculate pages per day
        progress["Reading Speed"] = progress["Pages"] / progress["Reading Days"]

        # sort by date started
        progress = progress.sort_values(by="Date Started")
        print(
            tabulate(
                progress[["Title", "Reading Days", "Reading Speed"]],
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
                floatfmt=".1f",
            )
        )
        return progress

    def time_to_finish_list(self):
        # filter out books that haven't been started
        progress = self.model.data[self.model.data["Date Started"].notna()]
        # convert to reading days
        progress["Reading Days"] = (
            progress["Date Finished"] - progress["Date Started"]
        ).dt.days
        # calculate reading speed
        progress["Reading Speed"] = progress["Pages"] / progress["Reading Days"]
        # calculate time to finish
        progress["Time to Finish"] = (
            progress["Pages"] - progress["Pages Read"]
        ) / progress["Reading Speed"]
        print(
            tabulate(
                progress[["Title", "Time to Finish"]],
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
            )
        )
        return progress

    def show_average_reading_speed(self):
        progress = self.show_reading_progress()
        self.show_read_unread_count()
        avg_speed = progress["Reading Speed"].mean()

        print(f"\nAverage reading speed: {avg_speed:.2f} pages/day")

    def show_read_unread_count(self):
        read_count = len(self.model.data[self.model.data["Date Finished"].notna()])
        unread_count = len(self.model.data[self.model.data["Date Finished"].isna()])
        print(f"\nBooks read: {read_count}, Books unread: {unread_count}")
