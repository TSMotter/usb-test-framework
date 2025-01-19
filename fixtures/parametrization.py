import pytest
import configparser
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


@pytest.fixture(scope="session", autouse=True)
def dd_cfg():
    config_path = os.path.join(os.path.dirname(
        os.getcwd()), "config", "parametrization.cfg")
    logger.info(
        f"Reading test parametrization settings from file: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['dd']


@pytest.fixture(scope="session", autouse=True)
def fio_cfg():
    config_path = os.path.join(os.path.dirname(
        os.getcwd()), "config", "parametrization.cfg")
    logger.info(
        f"Reading test parametrization settings from file: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['fio']
