import os
from docx import Document

def extract_images_from_docx(docx_path, output_dir):
    # Kiểm tra nếu đường dẫn đến file và thư mục tồn tại
    if not os.path.exists(docx_path):
        print(f"File {docx_path} không tồn tại.")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Đọc file Word
    doc = Document(docx_path)
    
    # Duyệt qua tất cả các phần tử trong tài liệu
    for i, rel in enumerate(doc.part.rels.values()):
        if "image" in rel.target_ref:
            img_data = rel.target_part.blob
            img_filename = f"image_{i + 1}.png"
            img_path = os.path.join(output_dir, img_filename)

            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"Đã lưu {img_filename} vào {output_dir}")

if __name__ == "__main__":
    docx_path = "d:\\tools\\dv\\tachimgdocs\\web.docx"  # Thay đổi đường dẫn đến file Word của bạn
    output_dir = "thu_muc_luu_anh"  # Thay đổi đường dẫn đến thư mục bạn muốn lưu hình ảnh
    extract_images_from_docx(docx_path, output_dir)
