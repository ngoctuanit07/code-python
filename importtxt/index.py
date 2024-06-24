import requests

def read_file_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def send_data_to_api(data):
    url = "https://demo.dongtamcorp.com/api/v1/importPost"
    payload = {"name": data}
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"Successfully sent: {data}")
    else:
        print(f"Failed to send: {data}. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    file_path = "data.txt"  # Đường dẫn tới file txt của bạn
    lines = read_file_line_by_line(file_path)
    
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:  # Chỉ gửi các dòng không rỗng
            send_data_to_api(cleaned_line)
