#!/bin/bash

DEVICE=$1

set -x

# Unmount the USB stick if mounted
sudo umount ${DEVICE}1

# Wipe the USB stick (write zeros to the entire device)
#sudo dd if=/dev/zero of=${DEVICE} bs=1M status=progress

# Create a new partition table
echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk ${DEVICE}

# Format the partition as ext4
sudo mkfs.ext4 ${DEVICE}1

# Mount the USB stick (optional, just for verification)
sudo mount ${DEVICE}1 /mnt

echo "USB stick ${DEVICE} has been formatted and mounted at /mnt"
