# qrcodetest.py
import qrcode
from PIL import Image

# ==== Hàm chuyển đổi mm → pixel ====
def mm_to_px(mm: float, dpi: int = 300) -> int:
    """Chuyển đổi mm sang pixel theo DPI."""
    return int(round((mm / 25.4) * dpi))

# ==== Cấu hình QR Code ====
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # tăng khả năng đọc khi in nhỏ
    box_size=10,
    border=0  # không thêm viền đen mặc định (ta tự thêm padding trắng)
)

# ==== Nội dung QR ====
qr.add_data("https://dongtamcorp.com")
qr.make(fit=True)

# ==== Tạo ảnh QR (đen trên nền trắng) ====
img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

# ==== Kích thước mong muốn (mm) ====
# LƯU Ý: dùng dấu chấm để biểu diễn số thập phân
target_width_mm = 29.092
target_height_mm = 20.927
padding_mm = 0.5                 # viền trắng 0.5mm quanh QR
dpi = 300

# ==== Chuyển sang pixel ====
target_width_px = mm_to_px(target_width_mm, dpi)
target_height_px = mm_to_px(target_height_mm, dpi)
padding_px = mm_to_px(padding_mm, dpi)

# ==== Resize QR đúng kích thước (giữ cạnh sắc bằng NEAREST) ====
# LANCZOS có thể làm mờ các ô vuông của QR; NEAREST giữ pixel cứng, máy quét đọc tốt hơn
img_qr = img_qr.resize((target_width_px, target_height_px), Image.NEAREST)

# ==== Tạo background trắng có viền ====
bg_width = target_width_px + padding_px * 2
bg_height = target_height_px + padding_px * 2
background = Image.new("RGB", (bg_width, bg_height), "white")

# Dán QR vào giữa nền (vì padding đều)
pos_x = padding_px
pos_y = padding_px
background.paste(img_qr, (pos_x, pos_y))

# ==== Xuất file JPG ====
output_file = "qrcode_web_14.587mm.jpg"
background.save(output_file, "JPEG", dpi=(dpi, dpi), quality=95, subsampling=0)

print(f"✅ QR code đã được tạo: {output_file}")
print(f"   - Kích thước QR: {target_width_mm} x {target_height_mm} mm")
print(f"   - Viền trắng: {padding_mm} mm mỗi bên")
print(f"   - Độ phân giải: {dpi} DPI")
print(f"   - Pixel QR: {target_width_px}x{target_height_px} px; Nền: {bg_width}x{bg_height} px")
