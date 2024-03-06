import tkinter as tk
from tkinter import ttk
import mysql.connector
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime
import io
from reportlab.lib.utils import ImageReader
from tkinter import messagebox
# Hàm tạo kết nối đến MySQL
def mysql_connection():
    return mysql.connector.connect(
        host="192.168.17.17",
        user="root",
        passwd="P@ssw0rd123",
        database="giant_ttxn"
    )

# Hàm truy vấn dữ liệu từ MySQL
def fetch_data(qrcode_from, qrcode_to):
    conn = mysql_connection()
    cursor = conn.cursor()
    if qrcode_to and qrcode_from:  # Nếu người dùng nhập cả Qrcode From và Qrcode To
        query = (
            "SELECT CONCAT(ID1, '-', Code) "
            "FROM receiptline "
            "WHERE ID1 >= %s AND ID1 <= %s AND CreatedDate >= %s AND IsDelete=0;"
        )
        cursor.execute(query, (qrcode_from, qrcode_to, f"{datetime.now().year}-01-01"))
    elif qrcode_from:  # Nếu người dùng chỉ nhập Qrcode From
        query = (
            "SELECT CONCAT(ID1, '-', Code) "
            "FROM receiptline "
            "WHERE ID1 >= %s AND CreatedDate >= %s AND IsDelete=0;"
        )
        cursor.execute(query, (qrcode_from, f"{datetime.now().year}-01-01"))
    else:  # Xử lý trường hợp không nhập gì hoặc chỉ nhập Qrcode To (tùy bạn thêm vào)
        return []
        
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# Hàm tạo và lưu QR Code vào PDF
def generate_pdf(data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"qrcode-{current_date}.pdf"  # Đặt tên file theo định dạng yêu cầu
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 2 * mm  # Lề cho mỗi bên
    usable_width = width - 10 * margin
    usable_height = height - 10 * margin
    
    qr_per_row = 4  # Số QR code trên mỗi hàng
    rows_per_page = 7  # Số hàng trên mỗi trang
    qr_width = usable_width / qr_per_row  # Chiều rộng của mỗi QR code
    qr_height = usable_height / rows_per_page  # Chiều cao của mỗi QR code, bao gồm cả chỗ cho label
    
    x_offset_start = margin
    y_offset_start = height - margin - qr_height
    x_offset = x_offset_start
    y_offset = y_offset_start

    for index, (code,) in enumerate(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        # Kiểm tra và bắt đầu hàng mới sau mỗi 4 QR codes
        if index % qr_per_row == 0 and index != 0:
            x_offset = x_offset_start
            y_offset -= qr_height

        # Kiểm tra và chuyển sang trang mới sau mỗi 20 QR codes (5 hàng * 4 QR code)
        if (index % (qr_per_row * rows_per_page) == 0 and index != 0) or y_offset < margin:
            c.showPage()
            x_offset = x_offset_start
            y_offset = y_offset_start

        # Vẽ QR code và label tương ứng
        c.drawImage(img_reader, x_offset, y_offset - 10 * mm, width=qr_width, height=qr_height - 10 * mm)  # Cập nhật để có chỗ cho label
        c.drawString(x_offset, y_offset - 15 * mm, code)  # Vẽ label dưới mỗi QR code, điều chỉnh vị trí nếu cần

        x_offset += qr_width  # Cập nhật x_offset cho QR code tiếp theo
    
    c.save()
    messagebox.showinfo("Thông báo", "Tạo file PDF thành công!")




# GUI
def on_generate_button_clicked():
    qrcode_from = from_entry.get()
    qrcode_to = to_entry.get()
    data = fetch_data(qrcode_from, qrcode_to)
    if data:
        generate_pdf(data)
    else:
        print("No data to generate QR codes. Please check your input.")

root = tk.Tk()
root.title("QR Code Generator")

tk.Label(root, text="QRCode From:").pack()
from_entry = tk.Entry(root)
from_entry.pack()

tk.Label(root, text="QRCode To:").pack()
to_entry = tk.Entry(root)
to_entry.pack()

generate_button = ttk.Button(root, text="Generate QR Codes", command=on_generate_button_clicked)
generate_button.pack()

root.mainloop()