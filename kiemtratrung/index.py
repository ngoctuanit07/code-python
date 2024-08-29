def find_duplicates(input_string):
    duplicates = {}
    for index, char in enumerate(input_string):
        if input_string.count(char) > 1:
            if char in duplicates:
                duplicates[char].append(index)
            else:
                duplicates[char] = [index]
    
    return duplicates

# Ví dụ sử dụng
input_string = "abracadabra"
duplicates = find_duplicates(input_string)

if duplicates:
    print("Các ký tự bị trùng và vị trí của chúng trong chuỗi là:")
    for char, positions in duplicates.items():
        print(f"Ký tự '{char}' bị trùng ở các vị trí: {positions}")
else:
    print("Không có ký tự nào bị trùng.")
