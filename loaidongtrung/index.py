def remove_duplicate_lines(file_path):
    try:
        # Đọc nội dung file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Loại bỏ các dòng trùng lặp
        unique_lines = list(set(lines))
        
        # Ghi lại các dòng không trùng lặp vào một file mới
        new_file_path = file_path.replace('.txt', '_unique.txt')
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.writelines(unique_lines)
        
        print(f"Đã loại bỏ các dòng trùng lặp. File mới được lưu tại: {new_file_path}")
    
    except FileNotFoundError:
        print("File không tồn tại. Vui lòng kiểm tra lại đường dẫn.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Ví dụ cách sử dụng
file_path = input("Nhập đường dẫn tới file txt: ")
remove_duplicate_lines(file_path)
