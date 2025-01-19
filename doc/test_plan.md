# Test Plan


## test_usb_stick::TestUSB::test_usb_stick_read_write_dump

- 1) Wipes and (re)partition the device
```sh
./scripts/wipe-and-format-usb.sh /dev/sdc
```

- 2) Create a random input bin file 
```sh
dd if=/dev/urandom of=/home/input.bin bs=1M count=100 status=progress
```

- 3) Calculate input bin file checksum

- 4) Write input bin file to usb stick
```sh
dd if=/home/input.bin of=/dev/sdb1 bs=1M seek=2048 conv=notrunc status=progress
```

- 5) Readback from usb stick
```sh
dd if=/dev/sdb1 of=/home/readback.bin skip=2048 bs=1M count=100 status=progress
```

- 6) Calculate and compare readout checksum

- 7) Compare checksums

- 8) Collect read/write metrics

- 9) Generate HTML report