import pymysql
import tkinter as tk
from tkinter import messagebox

# Hàm để kết nối với Database và thực hiện thêm mới
# Hàm để kết nối với Database và thực hiện thêm mới
def insert_into_database(name, name_english, med_exam_type, is_lh):
    # Chuyển đổi giá trị is_lh thành kiểu dữ liệu phù hợp với cột BIT trong MySQL
    is_lh_bit = b'1' if is_lh == '1' else b'0'

    # Tạo câu lệnh SQL đã hoàn chỉnh
    sql = """
    INSERT INTO `medicalexamine` (`ZoneID`, `Code`, `CodeUMC`, `MA_SO_NOI_BO`, `MA_TUONG_DUONG_7435`, `Name`, `NameEnglish`, `ShortName`, `NameForAnalysis`, `AliasNumber`, `Unit`, `Qty`, `PriceIn`, `PriceOut`, `PriceHoliday`, `PriceForeigner`, `PriceBHYT`, `PriceSurcharge`, `MedicalExamineCategoryID`, `DepartmentGroupID`, `PostingDate`, `CheckHealthInsurance`, `UserID`, `SoLanSuDung`, `MaKhoa`, `CreatedDate`, `EditedDate`, `EmployeeID`, `IsDelete`, `OldCode`, `ThongTu37`, `CounterUse`, `TextSearch`, `TextSearchEnglish`, `OrderNumber`, `loai_thu_thuat`, `DepartmentGroupIDShow`, `Sex`, `CommitmentType`, `ShortCode`, `MedicalExamineType`, `IsLH`) 
    VALUES ('HCM001', NULL, NULL, '2.1.0.9.03036', NULL, '{0}', '{1}', NULL, NULL, NULL, 'Lần', 1, NULL, NULL, NULL, NULL, NULL, NULL, 134, 110, NULL, NULL, NULL, NULL, NULL, '2024-01-26 14:22:28', '2024-01-26 14:29:31', NULL, {2}, NULL, NULL, 0, NULL, NULL, NULL, 0, 0, 2, NULL, NULL, '{3}', {4});
    """.format(name, name_english, is_lh_bit, med_exam_type, is_lh)



    connection = pymysql.connect(host='192.168.17.17',
                                 user='root',
                                 password='P@ssw0rd123',
                                 database='ttxn_dev',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        connection.close()


# Hàm xử lý khi nhấn nút Submit
def on_submit():
    name = entry_name.get()
    name_english = entry_name_english.get()
    med_exam_type = entry_med_exam_type.get()
    is_lh = entry_is_lh.get()

    # Kiểm tra và chuyển đổi giá trị is_lh
    if is_lh not in ['1', '0']:
        messagebox.showerror("Error", "Giá trị 'IsLH' không hợp lệ. Chỉ chấp nhận '1' hoặc '0'.")
        return

    insert_into_database(name, name_english, med_exam_type, is_lh)
    messagebox.showinfo("Info", "Thêm mới thành công")

# Tạo giao diện người dùng
root = tk.Tk()
root.title("Medical Examine Insert Form")

tk.Label(root, text="Name").grid(row=0)
tk.Label(root, text="Name English").grid(row=1)
tk.Label(root, text="Medical Examine Type").grid(row=2)
tk.Label(root, text="IsLH (1 or 0)").grid(row=3)

entry_name = tk.Entry(root)
entry_name_english = tk.Entry(root)
entry_med_exam_type = tk.Entry(root)
entry_is_lh = tk.Entry(root)

entry_name.grid(row=0, column=1)
entry_name_english.grid(row=1, column=1)
entry_med_exam_type.grid(row=2, column=1)
entry_is_lh.grid(row=3, column=1)

submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.grid(row=4, column=1)

root.mainloop()