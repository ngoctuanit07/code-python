import sys
import codecs
import random

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

def find_non_hex_chars(s):
    """
    Tìm tất cả các ký tự không phải là hexadecimal trong chuỗi.
    """
    non_hex_chars = [char for char in s if not char.isdigit() and char.lower() not in 'abcdef']
    return non_hex_chars

def fix_non_hex_chars(s):
    """
    Thay thế các ký tự không phải hexadecimal trong chuỗi bằng ký tự hexadecimal hợp lệ ngẫu nhiên.
    """
    hex_chars = "0123456789abcdef"
    fixed_string = ''.join(char if char.isdigit() or char.lower() in 'abcdef' else random.choice(hex_chars) for char in s)
    return fixed_string

def compare_and_fix_strings(string1, string2):
    """
    So sánh hai chuỗi và sửa chuỗi không hợp lệ thành hexadecimal hợp lệ.
    """
    result = {}

    # Kiểm tra và sửa chuỗi 1
    if is_hexadecimal(string1):
        result['string1'] = f"'{string1}' là một chuỗi hexadecimal hợp lệ."
    else:
        non_hex_chars1 = find_non_hex_chars(string1)
        fixed_string1 = fix_non_hex_chars(string1)
        result['string1'] = f"'{string1}' không phải là một chuỗi hexadecimal hợp lệ. Ký tự không hợp lệ: {non_hex_chars1}. Chuỗi đã sửa: {fixed_string1}"

    # Kiểm tra và sửa chuỗi 2
    if is_hexadecimal(string2):
        result['string2'] = f"'{string2}' là một chuỗi hexadecimal hợp lệ."
    else:
        non_hex_chars2 = find_non_hex_chars(string2)
        fixed_string2 = fix_non_hex_chars(string2)
        result['string2'] = f"'{string2}' không phải là một chuỗi hexadecimal hợp lệ. Ký tự không hợp lệ: {non_hex_chars2}. Chuỗi đã sửa: {fixed_string2}"

    return result

def main():
    while True:
        # Nhập chuỗi từ người dùng
        string1 = input("Nhập chuỗi thứ nhất (hoặc gõ 'exit' để thoát): ")
        if string1.lower() == 'exit':
            print("Chương trình kết thúc.")
            break

        string2 = input("Nhập chuỗi thứ hai (hoặc gõ 'exit' để thoát): ")
        if string2.lower() == 'exit':
            print("Chương trình kết thúc.")
            break

        # So sánh và sửa hai chuỗi
        result = compare_and_fix_strings(string1, string2)

        # In kết quả
        print(result['string1'])
        print(result['string2'])

if __name__ == "__main__":
    main()
