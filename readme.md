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

- Generate `blktrace` file and produce binary file with `blkparse` to replay that I/O profile with fio:
```sh
(.venvpy3) $ dd if=/dev/urandom of=$(pwd)/rand-bin.bin bs=4M count=250 status=progress
(.venvpy3) $ lsdev
/dev/sda  /dev/sda1  /dev/sda2  /dev/sda5  /dev/sdb  /dev/sdb1
----
/dev/sda5 on / type ext4 (rw,relatime,errors=remount-ro)
/dev/sda1 on /boot/efi type vfat (rw,relatime,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)
/dev/sdb1 on /media/ggm/USB_DRIVE type ext4 (rw,nosuid,nodev,relatime,uhelper=udisks2)
(.venvpy3) $ blktrace /dev/sdb
(terminal2) $ sudo cp rand-bin.bin /media/ggm/USB_DRIVE/
(.venvpy3) $ blkparse sdb -o dump.log
(.venvpy3) $ blkparse sdb -o /dev/null -d file-for-fio.bin
(.venvpy3) $ ls
file-for-fio.bin  rand-bin.bin  sdb.blktrace.0  sdb.blktrace.1  sdb.blktrace.2  sdb.blktrace.3  sdb.blktrace.4  sdb.blktrace.5
(.venvpy3) $ umount /dev/sdb1
(.venvpy3) $ lsdev
/dev/sda  /dev/sda1  /dev/sda2  /dev/sda5  /dev/sdb  /dev/sdb1
----
/dev/sda5 on / type ext4 (rw,relatime,errors=remount-ro)
/dev/sda1 on /boot/efi type vfat (rw,relatime,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)
(.venvpy3) $ fio --name=replay-from-trace --read_iolog=file-for-fio.bin
....
```

<!--

- 
```sh
```
-->