from streamlit.testing.v1 import AppTest
import os

os.environ["DATA_DIR"] = ".tmp"


def test_for_smoke():
    app_test = AppTest.from_file("main.py")
    app_test.run()
    assert not app_test.exception
