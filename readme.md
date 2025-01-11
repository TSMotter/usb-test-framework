# USB Test Framework

- Create py3 venv
```bash
sudo apt-get install python3.8-venv
python -m venv .venvpy3
```

- Activate the venv
```bash
source .venvpy3/bin/activate
```

- Install packages into the venv
```bash
pip install -r requirements.txt
```

- Configure `settings.cfg` with the appropriate USB stick information

- Connect the USB stick to the machine and "format it" to a new partition table and partition
```bash
sudo umount sdb1
echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk sdb
sudo mkfs.ext4 sdb1
```

- Run the tests
```bash
(.venvpy3) ggm@ubuntu2004:~/Documents/usb-test-framework/tests (master)$ pytest --log-cli-level=DEBUG -v test_usb_stick.py
```

- Cheatsheet
```bash
sudo fdisk -l /dev/sdb
sudo parted /dev/sdb print
```

- 
```bash
```