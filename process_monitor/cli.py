import typer
import psutil
import time
import traceback
import csv
import warnings

app = typer.Typer()

@app.command()
def processes():
    print("listing processes")
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        print(proc.info)

@app.command()
def monitor(process_name: str, duration_in_seconds: int, sampling_interval_in_seconds: int = 5, pid: int = -1):
    print("monitoring {}".format(process_name))
    cpu_usage_samples = []
    private_memory_samples = []
    open_file_descriptors_samples = []

    do_every(sampling_interval_in_seconds, duration_in_seconds, lambda: monitor_process(process_name, pid, cpu_usage_samples, private_memory_samples, open_file_descriptors_samples))
    
    print(cpu_usage_samples)
    print(private_memory_samples)
    print(open_file_descriptors_samples)

    if len(cpu_usage_samples) != 0 and len(private_memory_samples) != 0 and len(open_file_descriptors_samples) != 0:
        create_report(cpu_usage_samples, private_memory_samples, open_file_descriptors_samples)
        detect_memory_leak(private_memory_samples, process_name)

        print("CPU usage average for process {}: {}%".format(process_name, average(cpu_usage_samples)))
        print("Memory usage average for process {}: {}".format(process_name, average(private_memory_samples)))
        print("Open file descriptors average for process {}: {}".format(process_name, average(open_file_descriptors_samples)))

# execute task every interval for a duration
def do_every(interval: int, duration: int, task):
    start_time = time.time()
    next_time  = start_time + interval
    while time.time() - start_time < duration:
        time.sleep(max(0, next_time - time.time()))

        try:
            task()
        except psutil.AccessDenied:
            print("Access to the process denied - exiting monitoring process")
            traceback.print_exc()
            break
        except Exception:
            print("Encountered a problem while executing task")
            traceback.print_exc()

        # skip the task if the execution took longer then interval
        next_time += (time.time() - next_time) // interval * interval + interval

# find a process and extract its metrics
def monitor_process(name: str, pid: int, cpu_samples, memory_samples, file_samples):
    for process in psutil.process_iter():
        if process.name() == name and (pid == -1 or pid == process.pid):
            print("Monitoring process: {}".format(process.pid))
            with process.oneshot():
                cpu = process.cpu_percent()
                print("CPU %: {:.2f}".format(cpu))
                cpu_samples.append(cpu)
                mem = process.memory_full_info()
                print(mem)
                memory_samples.append(mem.uss)
                file = process.num_fds()
                print("Files: {}".format(file))
                file_samples.append(file)

def average(list: list[float]):
    return sum(list) / len(list)

# creates a csv report with collected metrics
def create_report(cpu_samples, memory_samples, file_samples):
    with open('report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        columns = ["cpu_percent", "private_memory", "open_file_descriptors"]
        
        writer.writerow(columns)
        
        for (cpu_sample, memory_sample, file_sample) in zip(cpu_samples, memory_samples, file_samples):
            writer.writerow([cpu_sample, memory_sample, file_sample])

# check if total private memory allocated by process is increasing
def detect_memory_leak(memory_samples, process_name):
    # zip() creates pairs of adjacent elements, all() checks if all elements satisfy the condition i < j, where i and j are elements of a pair
    is_memory_increasing_over_time = all(i < j for i, j in zip(memory_samples, memory_samples[1:]))
    if is_memory_increasing_over_time:
        message = "Potential memory leak in process: {}; allocated memory for the process is steadily increasing".format(process_name)
        warnings.warn(message)
    else:
        print("Memory leak not detected")