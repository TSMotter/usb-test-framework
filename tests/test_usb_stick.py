import pytest
import shutil
import hashlib
import subprocess
import os
import sys
import time
import logging
import json
from datetime import datetime

from fixtures.environment import testenv
from fixtures.parametrization import dd_cfg, fio_cfg
from fixtures.usb_stick import rand_bin_file, wipe_and_format_usb
from fixtures.reports import html_report_dd, report_fio

# Fixed number of test iterations
ITERATIONS = 10

# Setup logging to stdout and to a log file
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


@pytest.mark.usefixtures("wipe_and_format_usb")
class TestUSBdd:
    @staticmethod
    def calculate_md5sum(file_path):
        """Calculate MD5 checksum of a file"""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @pytest.mark.parametrize("iteration", range(ITERATIONS))
    def test_usb_stick_read_write_checksum(self, testenv, dd_cfg, iteration, html_report_dd, rand_bin_file):
        """Test USB reliability by writing and reading back data"""

        # Skip test if not running on Linux
        if sys.platform != "linux":
            pytest.skip("This test needs Linux OS to be executed")

        partition1 = testenv['usb']['device'] + "1"

        tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        readback_file = os.path.join(tmp_dir, f"readback_data_{iteration}.bin")

        expected_hash = self.calculate_md5sum(rand_bin_file)
        logger.info(f"This is the expected_hash: {expected_hash}")

        try:
            # Time the write operation
            command = f"dd if={rand_bin_file} of={partition1} bs={dd_cfg['bs']} seek={dd_cfg['offset']} conv=notrunc status=progress"
            logger.info(f"Will execute: {command}")
            start_write_time = time.time()
            subprocess.run(f"{command}", shell=True, check=True)
            write_duration = time.time() - start_write_time

            # Flush the disk to ensure data is written
            subprocess.run("sync", shell=True, check=True)
            time.sleep(3)

            # Time the read operation
            command = f"dd if={partition1} of={readback_file} bs={dd_cfg['bs']} skip={dd_cfg['offset']} count={dd_cfg['count']} status=progress"
            logger.info(f"Will execute: {command}")
            start_read_time = time.time()
            subprocess.run(f"{command}", shell=True, check=True)
            read_duration = time.time() - start_read_time

            # Calculate hash of read data
            actual_hash = self.calculate_md5sum(readback_file)
            logger.info(f"This is the actual_hash: {actual_hash}")

            # Log success/failure
            result_message = f"Iteration {iteration + 1}: "
            if expected_hash == actual_hash:
                result_message += f"SUCCESS (Hashes match - {expected_hash}) - Write time: {write_duration:.2f}s, Read time: {read_duration:.2f}s"
            else:
                result_message += f"FAILURE (Hashes do not match {expected_hash} != {actual_hash}) - Write time: {write_duration:.2f}s, Read time: {read_duration:.2f}s"

            # Log times spent
            logger.info(f"{result_message}")

        finally:
            logger.info(f"Finally block reached")
            shutil.rmtree(tmp_dir)

            success = expected_hash == actual_hash
            # Store result in class attribute
            html_report_dd.append({
                "iteration": iteration,
                "write_duration": write_duration,
                "read_duration": read_duration,
                "hash_match": success
            })


@pytest.mark.usefixtures("wipe_and_format_usb")
class TestUSBfio:
    @pytest.mark.parametrize("iteration", range(4))
    @pytest.mark.parametrize("rw", ["write", "randwrite"])
    @pytest.mark.parametrize("ioengine", ["sync", "libaio"])
    @pytest.mark.parametrize("iodepth", ["1", "16", "32"])
    @pytest.mark.parametrize("numjobs", ["1"])
    def test_fio_write_and_verify(self, request, devname,
                                  iteration, rw, ioengine, iodepth, numjobs,
                                  fio_cfg, testenv, report_fio):
        try:
            testname = request.node.name
            testcase = numjobs + '-' + iodepth + '-' + ioengine + '-' + rw
            command = f"fio \
                --name={testname} \
                --verify_state_save=0 \
                --direct=1 \
                --rw={rw} \
                --ioengine={ioengine} \
                --iodepth={iodepth} \
                --numjobs={numjobs} \
                --group_reporting \
                --bs=128k \
                --size={fio_cfg['size']} \
                --verify=crc32c \
                --filename={testenv['usb']['device']} \
                --output-format=json"
            logger.info(f"Will execute: {command}")
            res = subprocess.run(
                f"{command}", capture_output=True, shell=True, check=True)
            rc = res.returncode
            stdout = res.stdout.decode('utf-8')
            json_stdout = json.loads(stdout)
            job_summary = json_stdout['jobs'][-1]
            read = job_summary['read']
            write = job_summary['write']

            # Make sure json structure is OK
            if devname not in report_fio:
                report_fio[devname] = {}
            if testcase not in report_fio[devname]:
                report_fio[devname][testcase] = {}
            if iteration not in report_fio[devname][testcase]:
                report_fio[devname][testcase][iteration] = {}
            if 'read' not in report_fio[devname][testcase][iteration]:
                report_fio[devname][testcase][iteration]['read'] = {}
            if 'write' not in report_fio[devname][testcase][iteration]:
                report_fio[devname][testcase][iteration]['write'] = {}

            report_fio[devname][testcase][iteration]['success'] = rc
            report_fio[devname][testcase][iteration]['read']['io_kbytes'] = read['io_kbytes']
            report_fio[devname][testcase][iteration]['read']['bw'] = read['bw']
            report_fio[devname][testcase][iteration]['read']['iops'] = read['iops']
            report_fio[devname][testcase][iteration]['read']['runtime'] = read['runtime']
            report_fio[devname][testcase][iteration]['write']['io_kbytes'] = write['io_kbytes']
            report_fio[devname][testcase][iteration]['write']['bw'] = write['bw']
            report_fio[devname][testcase][iteration]['write']['iops'] = write['iops']
            report_fio[devname][testcase][iteration]['write']['runtime'] = write['runtime']
            report_fio[devname][testcase][iteration]['usr_cpu'] = job_summary['usr_cpu']
            report_fio[devname][testcase][iteration]['sys_cpu'] = job_summary['sys_cpu']

        except Exception as e:
            logger.warning(f"Except block reached: {e}")
            if rc != 0:
                stderr = res.stderr.decode('utf-8')
                logger.warning(f"This is rc: {rc}")
                logger.warning(f"This is stderr: {stderr}")
                pytest.fail("Exception happened!!!")
        finally:
            logger.info(f"Finally block reached")
