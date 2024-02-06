sheet_url = "https://docs.google.com/spreadsheets/d/1rn_RLco5KZFI6dLMSmcLdxrjNhG9n9az4fwNZUJ0F8c/edit#gid=0"
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cấu hình xác thực cho Google Sheets
# Cấu hình xác thực cho Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('hacano-0c76feb7748c.json', scope)
client = gspread.authorize(creds)

# Mở Google Sheet bằng ID
sheet = client.open_by_key(sheet_id)
worksheet = sheet.get_worksheet(0)  # Chọn sheet đầu tiên

# Đọc dữ liệu vào DataFrame
data = worksheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])  # Bỏ qua hàng tiêu đề

# Chọn cột cần thiết, giả sử tên cột chứa dữ liệu gia phả là 'family_name'
df = df[['family_name']].dropna()  # Loại bỏ hàng trống

# Lưu dữ liệu vào file txt
file_path = 'family_names.txt'
with open(file_path, 'w', encoding='utf-8') as file:
    for index, row in df.iterrows():
        family_name = row['family_name']
        file.write(f"{family_name}\n")

print(f"Đã lưu dữ liệu vào file '{file_path}' thành công.")
