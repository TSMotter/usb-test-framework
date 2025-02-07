import pytest


def pytest_addoption(parser):
    parser.addoption("--devname", action="store", default="no-devname")
    parser.addoption("--scene", action="store", default="scene1")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.devname
    if 'devname' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("devname", [option_value])
    option_value = metafunc.config.option.scene
    if 'scene' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("scene", [option_value])
