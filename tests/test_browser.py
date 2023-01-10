from os import wait
from src.browser import Browser
from unittest import mock
import pandas as pd
from dateutil.parser import parse


@mock.patch("pandas.read_sql", return_value=pd.DataFrame({"foo": [1, 2, 3]}))
def test_browser_init(mock_read_sql):
    # Test the init function
    test_browser = Browser(db_name="test.db")
    assert mock_read_sql.called
    assert test_browser is not None


@mock.patch("pandas.read_sql", return_value=pd.DataFrame({"foo": [1, 2, 3]}))
@mock.patch("src.browser.Browser.show_all_books")
@mock.patch("src.browser.Browser.show_books_by_author")
@mock.patch("src.browser.Browser.show_books_by_title")
@mock.patch("src.browser.Browser.show_books_by_id")
@mock.patch("src.browser.Browser.edit_book_details")
def test_browser_menu(mock_read_sql, mock_show_all_books, mock_show_books_by_author, mock_show_books_by_title, mock_show_books_by_id, mock_edit_book_details):
    # Test the menu function
    test_browser = Browser(db_name="test.db")
    with mock.patch("builtins.input", side_effect=["1", "2", "3", "4", "5", "q"]):
        test_browser.menu()
    assert mock_read_sql.called
    assert mock_show_all_books.called
    assert mock_show_books_by_author.called
    assert mock_show_books_by_title.called
    assert mock_show_books_by_id.called
    assert mock_edit_book_details.called

@mock.patch("pandas.read_sql", return_value=pd.DataFrame({"foo": [1, 2, 3]}))
def test_bowser_menu_invalid_choice(mock_read_sql):
    # Test the menu function
    test_browser = Browser(db_name="test.db")
    with mock.patch("builtins.input", side_effect=["6", "q"]):
        test_browser.menu()
    assert mock_read_sql.called

@mock.patch("pandas.read_sql", return_value=pd.DataFrame({"foo": [1, 2, 3]}))
def test_browser_show_all_books(mock_read_sql):
    # Test the show_all_books function
    test_browser = Browser(db_name="test.db")
    test_browser.data = pd.DataFrame(pd.Series(range(1, 101)))
    with mock.patch("builtins.input", return_value="a") as mock_input:
        test_browser.show_all_books()
    assert mock_read_sql.called
    assert mock_input.assert_called


@mock.patch(
    "pandas.read_sql",
    return_value=pd.DataFrame({"Author": ["foo", "bar", "baz", "qux", "quux"]}),
)
def test_browser_show_books_by_author(mock_read_sql):
    # Test the show_books_by_author function
    test_browser = Browser(db_name="test.db")
    with mock.patch("builtins.input", return_value="bar") as mock_input:
        found_books = test_browser.show_books_by_author()
        assert found_books["Author"].nunique() == 1
        assert mock_input.assert_called
        assert mock_read_sql.assert_called


@mock.patch(
    "pandas.read_sql",
    return_value=pd.DataFrame({"Title": ["foo", "bar", "baz", "qux", "quux"]}),
)
def test_browser_show_books_by_title(mock_read_sql):
    # Test the show_books_by_author function
    test_browser = Browser(db_name="test.db")
    with mock.patch("builtins.input", return_value="bar") as mock_input:
        found_books = test_browser.show_books_by_title()
        assert found_books["Title"].nunique() == 1
        assert mock_input.assert_called
        assert mock_read_sql.assert_called


@mock.patch("pandas.read_sql", return_value=pd.DataFrame({"index": [1, 2, 3, 4, 5]}))
def test_browser_show_books_by_id(mock_read_sql):
    # Test the show_books_by_author function
    test_browser = Browser(db_name="test.db")
    with mock.patch("builtins.input", return_value=3) as mock_input:
        found_books = test_browser.show_books_by_id()
        assert found_books["index"].nunique() == 1
        assert mock_input.assert_called
        assert mock_read_sql.assert_called


@mock.patch(
    "pandas.read_sql",
    return_value=pd.DataFrame(
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
    ),
)
def test_browser_edit_book_details(mock_read_sql):
    # Test the show_books_by_author function
    test_browser = Browser(db_name="test.db")
    with mock.patch(
        "builtins.input", side_effect=[3, "2022-05-13", "2022-6-13"]
    ) as mock_input:
        found_books = test_browser.edit_book_details()
        assert found_books.loc[found_books["index"] == 3, ["Date Started"]].values[0] == parse(
            "2022-05-13", fuzzy=True
        )
        assert found_books.loc[found_books["index"] == 3, ["Date Finished"]].values[0] == parse(
            "2022-06-13", fuzzy=True
        )
        assert mock_input.assert_called
        assert mock_read_sql.assert_called
