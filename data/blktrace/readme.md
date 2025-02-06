# blktrace data
- After doing some empirical experiments, it was possible to see that `blktrace` would indicate different throughputs depending on the lenght of time it was executed for
- For example, running the same test and fetching a trace with `timeout 60s blktrace /dev/sdb` or `timeout 120s blktrace /dev/sdb` would produce completely different throughput results in the 2 traces, simply because `blktrace` uses the time it was running for, to compute the throughput
- Because of that, all of the data here so far has been collected like so:
- Configure gnome-disks disk benchmark as is described in each folder's readme.md file
- This will lead to a benchmark that is expected to take a couple of minutes to reach the end
- Once the benchmark is running on the disk, on a different terminal, use `blktrace` to create a trace of the disk activity like this:
    - `timeout 60s blktrace /dev/sdb`
- Making it this way, `blktrace` will always run for the same amount of time in a scenario where the disk activity is more or less constant
