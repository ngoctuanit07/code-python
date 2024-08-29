import sys
import codecs

# Thay đổi mã hóa đầu ra của hệ thống thành UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
def is_hexadecimal(s):
    """
    Kiểm tra xem chuỗi có phải là một chuỗi hexadecimal hợp lệ không.
    Một chuỗi hexadecimal chỉ chứa các ký tự 0-9, a-f, hoặc A-F.
    """
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def main():
    while True:
        # Nhập chuỗi từ người dùng
        input_string = input("Nhập chuỗi để kiểm tra (hoặc gõ 'exit' để thoát): ")

        # Thoát khỏi chương trình nếu người dùng gõ 'exit'
        if input_string.lower() == 'exit':
            print("Chương trình kết thúc.")
            break

        # Kiểm tra chuỗi
        if is_hexadecimal(input_string):
            print(f"'{input_string}' là một chuỗi hexadecimal hợp lệ.")
        else:
            print(f"'{input_string}' không phải là một chuỗi hexadecimal hợp lệ.")

if __name__ == "__main__":
    main()
