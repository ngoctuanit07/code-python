import threading
import subprocess
import os

# Define the paths to your Node.js apps and main file name in each folder
node_app_paths = {
    "G:\\Game\\yescoinv3": "yes.js",
    "G:\\Game\\xkucoin": "x.js",
    "G:\\Game\\pitchtalk": "pitch.js"
}

# Function to run a Node.js app using the node command
def run_node_app(path, file_name):
    try:
        # Use subprocess.Popen for non-blocking execution
        subprocess.Popen(["node", file_name], cwd=path)
    except Exception as e:
        print(f"Error running app in {path}: {e}")

# Creating and starting a thread for each Node.js app
threads = []
for path, file_name in node_app_paths.items():
    thread = threading.Thread(target=run_node_app, args=(path, file_name))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All Node.js apps have been started concurrently.")
