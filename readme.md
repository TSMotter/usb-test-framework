# USB Test Framework

- Create py3 venv
```sh
sudo apt-get install python3.8-venv
python -m venv .venvpy3
```

- Activate the venv
```sh
source .venvpy3/bin/activate
```

- Install packages into the venv
```sh
pip install -r requirements.txt
```

- Format code
```sh
autopep8 . --recursive --in-place
```

- Configure `environment.cfg` with the appropriate USB stick information

- Connect the USB stick to the machine and "format it" to a new partition table and partition
```sh
sudo umount sdb1
echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk sdb
sudo mkfs.ext4 sdb1
```

- Run the tests
```sh
sudo su
source .venvpy3/bin/activate
cd tests
pytest --log-cli-level=DEBUG -v -k test_usb_stick.py
pytest --log-cli-level=DEBUG -v --devname=sandisk-32gb -k TestUSBfio
pytest --log-cli-level=DEBUG -v -k test_fio_write_and_verify
```

- Cheatsheet
```sh
sudo fdisk -l /dev/sdb
sudo parted /dev/sdb print
```

<!--

- 
```sh
```
-->