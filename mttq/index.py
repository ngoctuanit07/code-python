import tkinter as tk
from tkinter import messagebox
import requests
import io
import pdfplumber

# Hàm tải PDF từ URL và tìm kiếm tên
def search_in_pdf(name):
    url = 'https://bna.1cdn.vn/2024/09/13/thong_tin_ung_ho_qua_tsk_vcb_0011001932418_tu_01_09_den10_09_2024.pdf'
    
    # Tải file PDF từ URL
    response = requests.get(url)
    
    if response.status_code == 200:
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if name in text.upper():
                    # Tìm kiếm số tiền trong trang
                    result_line = ""
                    for line in text.split('\n'):
                        if name in line.upper():
                            result_line = line
                            break
                    
                    return result_line
    return None

# Hàm xử lý sự kiện tìm kiếm
def search_action():
    name = entry.get().upper()
    if name:
        result = search_in_pdf(name)
        if result:
            messagebox.showinfo("Kết quả tìm kiếm", f"Thông tin tìm thấy: {result}")
        else:
            messagebox.showinfo("Kết quả tìm kiếm", "Không tìm thấy thông tin!")
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên để tìm kiếm")

# Tạo giao diện bằng Tkinter
root = tk.Tk()
root.title("Tìm kiếm trong PDF")

# Label và Entry để nhập họ tên
label = tk.Label(root, text="Nhập họ tên:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# Button để thực hiện tìm kiếm
button = tk.Button(root, text="Tìm kiếm", command=search_action)
button.pack(pady=10)

# Chạy giao diện Tkinter
root.mainloop()
