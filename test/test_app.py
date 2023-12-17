from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.element_tree import ElementList, WidgetList
import pytest
import os
import shutil
from logic import env_vars

tmp_dir = '.tmp'


@pytest.fixture(autouse=True, scope="function")
def setup_test_environment():
    env_vars.override_value(env_data_folder=tmp_dir)

    if os.path.exists(env_vars.env_data_folder):
        shutil.rmtree(env_vars.env_data_folder)

    yield  # This allows the test to run

    # Teardown code: executed after the test ends
    shutil.rmtree(env_vars.env_data_folder)


def test_for_smoke():
    app_test = AppTest.from_file("main.py")
    app_test.run()
    assert not app_test.exception


def test_fake_model_on_startup():
    env_vars.reset_env_to_default(env_data_folder=tmp_dir)
    env_vars.print_debug()
    app_test = AppTest.from_file("main.py", default_timeout=300)
    app_test.run()
    print_debug(app_test)
    assert not app_test.exception
    select = app_test.selectbox('select_model_dropdown')
    assert select.value == 'Fake auto-reply model (demonstration)'


def print_debug(app_test):
    for attr_name in dir(app_test):
        # Avoid private attributes and methods
        if not attr_name.startswith("_"):
            attr = getattr(app_test, attr_name)
            # Check if the attribute is an instance of ElementList or WidgetList
            if isinstance(attr, (ElementList, WidgetList)) and len(attr) > 0:
                print(f"{attr_name} has {len(attr)} elements")
                for i, element in enumerate(attr):
                    print(f"  Element {i}: {element}")
            # Fallback to check for standard sequences
            elif isinstance(attr, (list, tuple)) and len(attr) > 0:
                print(f"{attr_name} has {len(attr)} elements")
                for i, element in enumerate(attr):
                    print(f"  Element {i}: {element}")
