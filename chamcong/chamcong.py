import pandas as pd
import pymysql

def read_data_from_excel(excel_file_path, sheet_name=0):
    """
    Đọc dữ liệu từ file Excel dựa trên TenMay.
    """
    # Đọc dữ liệu từ file Excel từ sheet cụ thể
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    # Lọc dữ liệu dựa trên TenMay
    filtered_df = df[df['TenMay'] == 'Máy MCC00002']

    # Chọn các cột cần thiết
    rows = filtered_df[['MaChamCong', 'NgayCham', 'GioCham']].values.tolist()
    return rows

def import_data_to_database(rows, db_config):
    """
    Import dữ liệu vào cơ sở dữ liệu.
    """
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        for row in rows:
            MachamCong, NgayCham, GioCham = row
            query = """INSERT INTO mitadata (MachamCong, NgayCham, GioCham) 
                       VALUES (%s, %s, %s)"""
            cursor.execute(query, (MachamCong, NgayCham, GioCham))

        conn.commit()
    except pymysql.MySQLError as e:
        print(f"SQL Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()




# Đường dẫn tới file Excel
excel_file_path = 'D:\\tools\\dv\\chamcong\\CheckInOut.xlsx'

# Thông tin kết nối cơ sở dữ liệu
db_config = {
    'host': '192.168.17.17',
    'user': 'root',
    'password': 'P@ssw0rd123',
    'database': 'maychamcong'
}

# Đọc dữ liệu từ Excel
rows = read_data_from_excel(excel_file_path)

# Import dữ liệu vào cơ sở dữ liệu
import_data_to_database(rows, db_config)
