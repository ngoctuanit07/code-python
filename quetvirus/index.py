import os
import subprocess

def scan_directory(directory):
    # Đường dẫn tới clamscan.exe, bạn cần điều chỉnh cho phù hợp
    clamwin_path = r"C:\\Program Files (x86)\\ClamWin\\bin\\clamscan.exe"
    
    if not os.path.exists(clamwin_path):
        raise FileNotFoundError("ClamWin khong duoc cai dat")
    
    if not os.path.isdir(directory):
        raise FileNotFoundError("thu muc quet khong ton tai")

    print(f"quet thu muc: {directory}")
    
    # Chạy lệnh clamscan
    try:
        result = subprocess.run([clamwin_path, "-r", directory], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    directory_to_scan = r"D:\\tools\\dv\\quetvirus\\source_20240630124501_lesa"
    results = scan_directory(directory_to_scan)
    
    # In kết quả quét
    print(results)
