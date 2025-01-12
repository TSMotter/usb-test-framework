# Test Plan


## test_usb_stick - TestUSB - test_usb_stick_read_write_dump

- Given that the device is partitioned with a single partition which comprises of it's full size
```sh
/dev/sdb
# Only partition of 32G
/dev/sdb1
```

- Make sure that the device's partition 1 is not mounted
```sh
umount /dev/sdb1
```

- Write all zeros to the region (blank canvas)
```sh
dd if=/dev/zero of=/dev/sdb1 bs=1M seek=2048 count=100 conv=notrunc status=progress
```

- Create (if it does not exist) the random input bin file 
```sh
dd if=/dev/urandom of=/home/input.bin bs=1M count=100 status=progress
```

- Calculate input checksum

- Write it to usb stick
```sh
dd if=/home/input.bin of=/dev/sdb1 bs=1M seek=2048 conv=notrunc status=progress
```

- Readback from usb stick
```sh
dd if=/dev/sdb1 of=/home/readback.bin skip=2048 bs=1M count=100 status=progress
```

- Calculate and compare readout checksum

