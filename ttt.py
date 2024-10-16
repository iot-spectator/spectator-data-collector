import threading
import time

flag = True

def print_numbers():
    while flag is True:
        print(1)
        time.sleep(1)

# Create two threads
thread1 = threading.Thread(target=print_numbers)

# Start the threads
thread1.start()

flag = False

# Wait for both threads to complete
thread1.join()

print("Both threads have finished execution.")
