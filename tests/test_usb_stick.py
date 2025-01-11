import pytest
import hashlib
import subprocess
import os
import sys
import time
import logging
from datetime import datetime

from fixtures.usb_stick import usb_cfg, test_cfg, dd_cfg, \
    check_input_file_exists_or_create_it, unmount_device

# Fixed number of test iterations
ITERATIONS = 1

# Setup logging to stdout and to a log file
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

@pytest.mark.usefixtures("check_input_file_exists_or_create_it", "unmount_device")
class TestUSB:
    @staticmethod
    def calculate_md5sum(file_path):
        """Calculate MD5 checksum of a file"""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @pytest.mark.parametrize("iteration", range(ITERATIONS))
    def test_usb_stick_read_write_dump(self, iteration, usb_cfg, test_cfg, dd_cfg):
        """Test USB reliability by writing and reading back data"""

        # Skip test if not running on Linux
        if sys.platform != "linux":
            pytest.skip("This test needs Linux OS to be executed")

        partition1 = usb_cfg["device"] + "1"

        tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        readback_file = os.path.join(tmp_dir, f"readback_data_{iteration}.bin")

        expected_hash = self.calculate_md5sum(test_cfg['input_bin_file'])

        try:
            # Time the write operation
            start_write_time = time.time()
            subprocess.run(f"dd if={test_cfg['input_bin_file']} of={partition1} bs={dd_cfg['bs']} seek={dd_cfg['seek']} conv=notrunc status=progress", shell=True, check=True)
            write_duration = time.time() - start_write_time

            # Flush the disk to ensure data is written
            subprocess.run("sync", shell=True, check=True)

            # Time the read operation
            start_read_time = time.time()
            subprocess.run(f"dd if={partition1} of={readback_file} bs={dd_cfg['bs']} count={dd_cfg['count']} status=progress", shell=True, check=True)
            read_duration = time.time() - start_read_time

            # Calculate hash of read data
            actual_hash = self.calculate_md5sum(readback_file)

            # Log success/failure
            result_message = f"Test {iteration + 1}: "
            if expected_hash == actual_hash:
                result_message += f"SUCCESS (Hashes match) - Write time: {write_duration:.2f}s, Read time: {read_duration:.2f}s"
            else:
                result_message += f"FAILURE (Hashes do not match) - Write time: {write_duration:.2f}s, Read time: {read_duration:.2f}s"
            
            # Log times spent
            logger.info(f"Iteration {iteration}: {result_message}")

        finally:
            os.remove(tmp_dir)