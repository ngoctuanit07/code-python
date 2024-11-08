from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

app = Flask(__name__)

# Đường dẫn đến tệp ảnh gốc
input_image_path = 'E:\\Inthe\\Card-DIAMOND.jpg'

# Hàm để thêm văn bản vào hình ảnh
def add_text_to_image(image, card_info):
    draw = ImageDraw.Draw(image)
    # Định nghĩa font (đảm bảo font tồn tại hoặc chỉ định đường dẫn đầy đủ đến font)
    font = ImageFont.truetype("arial.ttf", 28)

    # Tọa độ cho từng thông tin cần vẽ (điều chỉnh theo layout ảnh)
    coordinates = {
        "Mã số thẻ": (195, 145),  # Vị trí tương ứng trên ảnh
        "Họ và tên": (195, 239),
        "Nha khoa": (195, 315),
        "Bệnh lý": (195, 415)
    }

    # Vẽ từng thông tin lên hình
    for key, value in card_info.items():
        if key in coordinates:
            draw.text(coordinates[key], value, font=font, fill="black")

    return image

@app.route('/generate-card', methods=['POST'])
def generate_card():
    # Lấy dữ liệu JSON từ POST request
    card_info = request.get_json()

    # Kiểm tra dữ liệu JSON
    if not card_info:
        return jsonify({"error": "Invalid input data"}), 400

    try:
        # Mở ảnh gốc
        image = Image.open(input_image_path)

        # Thêm văn bản vào ảnh
        modified_image = add_text_to_image(image.copy(), card_info)

        # Chuyển đổi ảnh sang base64
        buffered = BytesIO()
        modified_image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Trả về chuỗi base64 trong JSON
        return jsonify({"image_base64": "data:image/jpeg;base64," + img_base64})

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": "Error processing image"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
