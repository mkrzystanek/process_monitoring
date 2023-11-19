import time

def explicit_memory_leak():
    print("creating memory leak")
    data = []
    while True:
        data.append([1] * 1000000)
        time.sleep(3)

explicit_memory_leak()
