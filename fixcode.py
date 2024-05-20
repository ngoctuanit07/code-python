import subprocess
import os

def phpcs_check(directory):
    # Đường dẫn tuyệt đối đến phpcs
    phpcs_path = r'C:\Users\VACNGQU005\AppData\Roaming\Composer\vendor\bin\phpcs'
    result = subprocess.run([phpcs_path, '--standard=PHPCompatibility', '--runtime-set', 'testVersion', '8.2-', directory], capture_output=True, text=True)
    if result.stdout:
        print("PHP syntax check results:")
        print(result.stdout)
    else:
        print("No syntax errors were found.")

def phpcbf_fix(directory):
    # Đường dẫn tuyệt đối đến phpcbf
    phpcbf_path = r'C:\Users\VACNGQU005\AppData\Roaming\Composer\vendor\bin\phpcbf'
    result = subprocess.run([phpcbf_path, '--standard=PHPCompatibility', '--runtime-set', 'testVersion', '8.2-', directory], capture_output=True, text=True)
    if result.stdout:
        print("Results of automatic error correction:")
        print(result.stdout)
    else:
        print("No errors to fix or all fixes completed.")

if __name__ == "__main__":
    source_directory = input("Enter the path to the PHP source code directory: ")
    if os.path.exists(source_directory):
        phpcs_check(source_directory)
        if input("Do you want to automatically fix errors (y/n)? ") == 'y':
            phpcbf_fix(source_directory)
    else:
        print("Path does not exist. Please check again.")