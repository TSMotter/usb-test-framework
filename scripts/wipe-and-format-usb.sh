#!/bin/bash

# Set the device path
DEVICE=$1

if [ "$DEVICE" == "/dev/sda" ]; then
  echo "DEVICE is /dev/sda. Exiting for safety reasons"
  exit 1
fi

# Unmount all partitions on the device
echo "Unmounting all partitions on $DEVICE..."
umount "${DEVICE}"* 2>/dev/null

# Wipe the partition table
echo "Wiping the partition table..."
wipefs --all --force "$DEVICE"
dd if=/dev/zero of="$DEVICE" bs=1M count=10 status=progress

# Create a new partition table (GPT)
echo "Creating a new GPT partition table..."
parted --script "$DEVICE" mklabel gpt

# Create a single ext4 partition
echo "Creating a new ext4 partition..."
parted --script "$DEVICE" mkpart primary ext4 0% 100%

# Format the partition to ext4
PARTITION="${DEVICE}1"
echo "Formatting $PARTITION to ext4..."
mkfs.ext4 -F "$PARTITION"

# Optional: Add a label to the filesystem
LABEL="USB_DRIVE"
echo "Adding label $LABEL to $PARTITION..."
e2label "$PARTITION" "$LABEL"

echo "Format complete. $DEVICE is now a single ext4 partition with label $LABEL."
