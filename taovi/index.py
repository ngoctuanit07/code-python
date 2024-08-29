from bit import Key
import sys
import codecs

# Thay đổi mã hóa đầu ra của hệ thống thành UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Hàm để chuyển đổi chuỗi đầu vào thành hexadecimal hợp lệ
def convert_to_hexadecimal(input_string):
    # Chuyển mỗi ký tự trong input_string thành mã ASCII rồi chuyển sang hexadecimal
    hexadecimal_string = ''.join(format(ord(c), '02x') for c in input_string)
    
    # Nếu độ dài chuỗi không đủ 64 ký tự (32 byte), cần thêm vào cho đủ
    if len(hexadecimal_string) < 64:
        hexadecimal_string = hexadecimal_string.ljust(64, '0')  # Thêm '0' ở cuối cho đủ 64 ký tự
    elif len(hexadecimal_string) > 64:
        hexadecimal_string = hexadecimal_string[:64]  # Cắt bớt nếu vượt quá 64 ký tự

    return hexadecimal_string

# Hàm để tạo ví Bitcoin từ chuỗi đầu vào
def create_btc_wallet_from_string(input_string):
    # Chuyển chuỗi đầu vào thành khóa riêng hexadecimal hợp lệ
    private_key = "bc18fdc730a8365682d82e9d0837adb9d68d0f57079824a790ec5ee49c1c97" #convert_to_hexadecimal(input_string)
    
    # Tạo ví Bitcoin từ khóa riêng
    key = Key.from_hex(private_key)
    
    # Lấy địa chỉ ví Bitcoin và khóa riêng
    wallet_address = key.address
    wif = key.to_wif()  # Wallet Import Format (WIF) của khóa riêng
    
    return wallet_address, wif

# Chuỗi đầu vào của bạn
input_string = "bc1qjasf9z3h7w3jspkhtgatx45vvzgpa2wwd2lr0eh5tx44reyn2k7sfc27a4"

# Tạo địa chỉ ví
address, wif = create_btc_wallet_from_string(input_string)

print(f"Địa chỉ ví BTC: {address}")
print(f"Khóa riêng (WIF): {wif}")
