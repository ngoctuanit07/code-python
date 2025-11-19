import pandas as pd
import os
import pyexcel as p

def read_pseudo_excel(path):
    """Đọc file giả Excel (tab / csv / text), tự động nhận encoding và delimiter"""
    rows = []

    encodings = ['utf-8', 'utf-16', 'utf-8-sig', 'cp1252', 'latin1']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                lines = f.readlines()
            print(f"✅ Đọc file thành công với encoding: {enc}")
            break
        except Exception:
            lines = []
            continue

    if not lines:
        raise Exception("❌ Không thể đọc được file với bất kỳ encoding nào!")

    # Tự động phát hiện delimiter
    first_line = lines[0]
    delimiter = '\t' if '\t' in first_line else ';' if ';' in first_line else ','

    # Chuẩn hóa dữ liệu
    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cols = line.split(delimiter)
        rows.append(cols)

    # Đồng bộ số cột
    max_cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < max_cols:
            r.append('')

    headers = rows[0]
    data = rows[1:]
    df = pd.DataFrame(data, columns=headers)
    return df

def convert_to_real_xls(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ File không tồn tại: {input_path}")
        return

    print(f"🔍 Đang đọc file: {input_path}")
    df = read_pseudo_excel(input_path)

    # Ghi ra file .xls thật bằng pyexcel
    records = df.to_dict(orient="records")
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    p.save_as(records=records, dest_file_name=output_path)
    print(f"✅ Đã tạo file Excel thật (.xls): {output_path}")

if __name__ == "__main__":
    # 🔧 Cấu hình file input / output
    input_path = r"D:\tools\dv\convertfilexcel\181025 KQ HBV.xls"
    output_path = r"D:\tools\dv\convertfilexcel\KQ_HBV_converted.xls"

    convert_to_real_xls(input_path, output_path)
