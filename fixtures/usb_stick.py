import pytest
import os
import subprocess
import logging

from .environment import testenv
from .parametrization import dd_cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


@pytest.fixture(scope="function")
def rand_bin_file(dd_cfg):
    rand_bin_file = os.path.join(os.path.dirname(os.getcwd()),
                                 "workspace",
                                 "rand_input.bin")

    logger.info(f"Creating file {rand_bin_file}")
    if os.path.exists(rand_bin_file):
        os.remove(f"{rand_bin_file}")
    subprocess.run(f"dd if=/dev/urandom \
                    of={rand_bin_file} \
                    bs={dd_cfg['bs']} \
                    count={dd_cfg['count']} \
                    status=progress",
                   shell=True, check=True)
    yield rand_bin_file
    os.remove(f"{rand_bin_file}")


@pytest.fixture(scope="class")
def wipe_and_format_usb(testenv):
    wipe_script = os.path.join(os.path.dirname(os.getcwd()),
                               "scripts",
                               "wipe-and-format-usb.sh")
    logger.info(f"Wiping and formating USB device with {wipe_script}")
    subprocess.run(
        f"sh {wipe_script} {testenv['usb']['device']}", shell=True, check=True)


@pytest.fixture(scope="function")
def file_for_fio(scene):
    scene_path = os.path.join(os.path.dirname(os.getcwd()),
                              "data",
                              "blktrace",
                              scene,
                              "file-for-fio.bin")
    logger.info(f"This is scene_path: {scene_path}")
    return scene_path


@pytest.fixture(scope="function")
def scene_info(scene):
    scene_path = os.path.join(os.path.dirname(os.getcwd()),
                              "data",
                              "blktrace",
                              scene,
                              "readme.md")

    description = ''
    with open(scene_path, "r") as f:
        device = f.readline()
        content = f.read().splitlines()
        description = '-'.join(content)
        description = description.replace(' ', '_')

    logger.info(f"This is scene_info: {description}")
    return {'device': device, 'description': description}
