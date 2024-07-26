import requests

def read_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def send_data_to_api(full_name):
    url = "https://dongqueson.dongtamcorp.com/api/adduser"
    payload = {
        "FullName": full_name,
        "ZoneID": "QNa002"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def main(file_path):
    data = read_data_from_file(file_path)
    for line in data:
        response = send_data_to_api(line)
        print(response)

if __name__ == "__main__":
    file_path = "D:\\tools\\dv\\vieta\\update_nv\\input.txt"  # Thay thế đường dẫn tới file txt của bạn
    main(file_path)