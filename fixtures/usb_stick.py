import pytest
import configparser
import os
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

@pytest.fixture(scope="session")
def usb_cfg():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.cfg")
    logger.debug(f"Reading USB config - from file: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    for item in config["USB"]:
        logger.debug(f"USB config: {item}")
    return config["USB"]

@pytest.fixture(scope="session")
def test_cfg():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.cfg")
    logger.debug(f"Reading TEST config - from file: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    logger.debug(f"Reading TEST config - content: {config}")
    return config["TEST"]

@pytest.fixture(scope="session")
def dd_cfg():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.cfg")
    logger.debug(f"Reading DD config - from file: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    logger.debug(f"Reading DD config - content: {config}")
    return config["DD"]

@pytest.fixture(scope="class")
def check_input_file_exists_or_create_it(dd_cfg, test_cfg):
    if not os.path.exists(test_cfg['input_bin_file']):
        logger.info(f"File does NOT exist: {test_cfg['input_bin_file']}")
        logger.info(f"Creating file: {test_cfg['input_bin_file']}")
        subprocess.run(f"dd if=/dev/urandom \
                       of={test_cfg['input_bin_file']} \
                       bs={dd_cfg['bs']} \
                       count={dd_cfg['count']} \
                       status=progress",
                       shell=True, check=True)

@pytest.fixture(scope="class")
def unmount_device(usb_cfg):
    def is_device_mounted(device):
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True, check=True)
            return any(device in line for line in result.stdout.splitlines())
        except subprocess.CalledProcessError:
            return False

    partition1 = usb_cfg['device'] + "1"
    if is_device_mounted(partition1):
        try:
            subprocess.run(['umount', partition1], check=True)
            logger.info(f"Device {partition1} unmounted successfully.")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to unmount {partition1}: {e}")
    else:
        logger.info(f"Device {partition1} is not mounted.")
