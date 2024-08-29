import sys
import codecs

# Thay đổi mã hóa đầu ra của hệ thống thành UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
def format_to_hexadecimal(input_string):
    """
    Format một chuỗi thành hexadecimal hợp lệ mà không thay đổi định dạng của chuỗi ban đầu.
    Thay thế các ký tự không phải hexadecimal bằng '0'.
    """
    hex_chars = "0123456789abcdefABCDEF"
    formatted_string = ""
    
    for char in input_string:
        if char in hex_chars:
            formatted_string += char
        else:
            formatted_string += '0'  # Thay thế ký tự không hợp lệ bằng '0'
    
    return formatted_string

def main():
    while True:
        # Nhập chuỗi từ người dùng
        input_string = input("Nhập chuỗi để format (hoặc gõ 'exit' để thoát): ")

        # Thoát khỏi chương trình nếu người dùng gõ 'exit'
        if input_string.lower() == 'exit':
            print("Chương trình kết thúc.")
            break

        # Format chuỗi thành hexadecimal hợp lệ
        formatted_string = format_to_hexadecimal(input_string)
        print(f"Chuỗi đã format: {formatted_string}")

if __name__ == "__main__":
    main()
