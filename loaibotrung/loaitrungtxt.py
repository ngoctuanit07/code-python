from collections import OrderedDict

def remove_duplicate_lines(input_file, output_file):
    # Sử dụng OrderedDict để lưu trữ các dòng duy nhất và giữ nguyên thứ tự
    unique_lines = OrderedDict()

    # Đọc nội dung từ tệp đầu vào
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            unique_lines[stripped_line] = None

    # Ghi các dòng duy nhất vào tệp đầu ra
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in unique_lines.keys():
            file.write(line + '\n')

# Tên tệp đầu vào và đầu ra
input_file = 'input.txt'
output_file = 'output.txt'

# Gọi hàm để loại bỏ các dòng trùng lặp
remove_duplicate_lines(input_file, output_file)
