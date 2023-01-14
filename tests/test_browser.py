from src.browser import Browser
from src.model import Model
from unittest import mock
import pandas as pd
from dateutil.parser import parse

# Instance of Browser class with mocked Model Class
def browser():
    with mock.patch.object(Model, "__init__", return_value=None):
        with mock.patch.object(Model, "read_data_from_db", return_value="test.db"):
            browser = Browser("path/to/config")
            browser.model = mock.create_autospec(Model)
            return browser


test_browser = browser()


def test_browser_init():
    # Test the init function
    with mock.patch.object(Model, "__init__", return_value=None) as mock_init:
        with mock.patch.object(Model, "read_data_from_db") as mock_read:
            test_browser = Browser(config="path/to/config")
            assert mock_init.called
            assert mock_read.called
            assert test_browser is not None


@mock.patch("src.browser.Browser.show_all_books")
@mock.patch("src.browser.Browser.show_books_by_author")
@mock.patch("src.browser.Browser.show_books_by_title")
@mock.patch("src.browser.Browser.show_books_by_id")
@mock.patch("src.browser.Browser.edit_book_details")
def test_browser_menu(
    mock_show_all_books,
    mock_show_books_by_author,
    mock_show_books_by_title,
    mock_show_books_by_id,
    mock_edit_book_details,
):
    # Test the menu function
    with mock.patch("builtins.input", side_effect=["1", "2", "3", "4", "5", "q", "n"]):
        test_browser.menu()
    assert mock_show_all_books.called
    assert mock_show_books_by_author.called
    assert mock_show_books_by_title.called
    assert mock_show_books_by_id.called
    assert mock_edit_book_details.called


def test_bowser_menu_invalid_choice():
    # Test the menu function
    with mock.patch("builtins.input", side_effect=["7", "q"]):
        with mock.patch.object(Browser, "save_and_exit") as mock_save:
            test_browser.menu()
    assert mock_save.called


def test_browser_show_all_books():
    # Test the show_all_books function
    test_browser.model.data = pd.DataFrame(pd.Series(range(1, 101)))
    with mock.patch("builtins.input", return_value="a") as mock_input:
        test_browser.show_all_books()
    assert mock_input.assert_called


@mock.patch(
    "pandas.read_sql",
    return_value=pd.DataFrame({"Author": ["foo", "bar", "baz", "qux", "quux"]}),
)
def test_browser_show_books_by_author(mock_read_sql):
    # Test the show_books_by_author function
    test_browser.model.data = pd.DataFrame(
        {"Author": ["foo", "bar", "baz", "qux", "quux"]}
    )
    with mock.patch("builtins.input", return_value="bar") as mock_input:
        found_books = test_browser.show_books_by_author()
        assert found_books["Author"].nunique() == 1
        assert mock_input.assert_called
        assert mock_read_sql.assert_called


def test_browser_show_books_by_title():
    # Test the show_books_by_author function
    test_browser.model.data = pd.DataFrame(
        {"Title": ["foo", "bar", "baz", "qux", "quux"]}
    )
    with mock.patch("builtins.input", return_value="bar") as mock_input:
        found_books = test_browser.show_books_by_title()
        assert found_books["Title"].nunique() == 1
        assert mock_input.assert_called


def test_browser_show_books_by_id():
    # Test the show_books_by_author function
    test_browser.model.data = pd.DataFrame({"index": [1, 2, 3, 4, 5]})
    with mock.patch("builtins.input", return_value=3) as mock_input:
        found_books = test_browser.show_books_by_id()
        assert found_books["index"].nunique() == 1
        assert mock_input.assert_called


def test_browser_edit_book_details():
    # Test the show_books_by_author function
    test_browser.model.data = pd.DataFrame(
        {
            "index": [1, 2, 3, 4, 5],
            "Date Started": [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2020-01-05",
            ],
            "Date Finished": [
                "2020-02-01",
                "2020-02-02",
                "2020-02-03",
                "2020-02-04",
                "2020-02-05",
            ],
        }
    )

    # Enter new dates for book 3
    with mock.patch(
        "builtins.input", side_effect=[3, "2022-05-13", "2022-6-13"]
    ) as mock_input:
        found_books = test_browser.edit_book_details()
        assert found_books.loc[found_books["index"] == 3, ["Date Started"]].values[
            0
        ] == parse("2022-05-13", fuzzy=True)
        assert found_books.loc[found_books["index"] == 3, ["Date Finished"]].values[
            0
        ] == parse("2022-06-13", fuzzy=True)
        assert mock_input.assert_called


def test_save_and_exit():
    # Test the exit_and_save function
    with mock.patch("builtins.input", return_value="y") as mock_input:
        with mock.patch.object(Browser, "update_kpi") as mock_convert:
            test_browser.save_and_exit()
            assert mock_input.called


def test_save_and_exit_exception():
    # Test the exit and save function with sqlite3 exception
    with mock.patch("builtins.input", return_value="y") as mock_input:
        return_value = test_browser.save_and_exit()
        assert mock_input.assert_called
        assert return_value == False


# def test_update_kpi():
#     # Test the update_kpi function
#     test_browser = Browser(config="config/test_config.yaml")
#     test_browser.model.data = pd.DataFrame(
#         {
#             "Date Started": ["2020-01-01", "2020-01-02"],
#             "Date Finished": ["2020-02-01", "2020-02-02"],
#             "Pages": [230, 240],
#         }
#     )
#     test_browser.model.data = test_browser.model.convert_columns_to_datetime(
#         ["Date Started", "Date Finished"]
#     )
#     test_browser.update_kpi()
#     assert test_browser.model.data["Days Read"].values[0] == 31
#     assert test_browser.model.data["Days Read"].values[1] == 31
#     assert 7.42 == pytest.approx(
#         test_browser.model.data["Pages per Day"].values[0], 0.1
#     )
#     assert 7.49 == pytest.approx(
#         test_browser.model.data["Pages per Day"].values[1], 0.1
#    )


def test_update_kpi():
    # Create test data
    data = {
        "Date Started": ["2020-01-01", "2020-01-05", "2020-01-15"],
        "Date Finished": ["2020-01-05", "2020-01-10", "2020-01-20"],
        "Pages": [100, 200, 300],
    }
    test_browser.model.data = pd.DataFrame(data)

    # Convert columns to datetime
    test_browser.model.data["Date Started"] = pd.to_datetime(
        test_browser.model.data["Date Started"]
    )
    test_browser.model.data["Date Finished"] = pd.to_datetime(
        test_browser.model.data["Date Finished"]
    )
    # Call the method being tested

    test_browser.update_kpi()

    # Assert that the new columns have been added
    assert "Days Read" in test_browser.model.data.columns
    assert "Pages per Day" in test_browser.model.data.columns

    # Assert that the values in the new columns are correct
    assert test_browser.model.data["Days Read"].tolist() == [4, 5, 5]
    assert test_browser.model.data["Pages per Day"].tolist() == [25.0, 40.0, 60.0]
