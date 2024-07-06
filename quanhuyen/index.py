import pandas as pd

# Đọc dữ liệu từ file Excel
file_path = 'TinhHuyenXa2021.xlsx'  # Đường dẫn tới file Excel của bạn
df = pd.read_excel(file_path)

# Tạo cấu trúc dữ liệu để lưu trữ thông tin tỉnh, huyện, xã
data = {}

for index, row in df.iterrows():
    tinh = row['Tỉnh Thành Phố']
    huyen = row['Quận Huyện']
    xa = str(row['Phường Xã'])  # Chuyển giá trị 'Phường Xã' thành chuỗi
    
    if tinh not in data:
        data[tinh] = {}
    if huyen not in data[tinh]:
        data[tinh][huyen] = []
    data[tinh][huyen].append(xa)

# Tạo file PHP và ghi dữ liệu vào
with open('data.php', 'w', encoding='utf-8') as f:
    f.write("<?php\n")
    f.write("return [\n")
    
    for tinh, huyen_dict in data.items():
        f.write(f'    "{tinh}" => [\n')
        for huyen, xa_list in huyen_dict.items():
            xa_str = '", "'.join(xa_list)
            f.write(f'        "{huyen}" => ["{xa_str}"],\n')
        f.write("    ],\n")
    
    f.write("];\n")
