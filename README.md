# This is an application for monitoring the process resources.

## Application supports two commands:
 - processes: lists all running processes.
 - monitor: takes samples of CPU and memory utilization as well as open file descriptors for a given process over a given amount of time. After the monitoring time is finished, a csv report is created, that contains all collected samples. The average values for monitored statistics are printed on the screen. Additionally, a warning is displayed on the screen, if a potential memory leak is detected.

 ## How to test the app:

 - build docker image `docker build --pull --rm -f "Dockerfile" -t nexthinkassignement:latest "."`
 - run the container in interactive mode `docker run --rm -it  nexthinkassignement:latest`
 - execute `python3 ./test/memory_leak.py &` command. The process pid will be printed on the screen.
 - execute `python3 -m process_monitor monitor python3 <duration of monitoring in seconds> --pid <memory process pid>`

## Additional notes

Application can be executed on Linux operating systems.

For process monitoring the `psutil` library was used. For details of the used methods output please refer to `psutil` [documentation](https://psutil.readthedocs.io/en/latest)  