import requests
from bs4 import BeautifulSoup
import os

def download_image(image_url, save_path):
    # Tải hình ảnh từ URL
    response = requests.get(image_url)
    
    # Kiểm tra xem yêu cầu tải hình ảnh thành công không
    if response.status_code == 200:
        # Lưu hình ảnh vào tệp cục bộ
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("Hình ảnh đã được tải và lưu thành công.")
    else:
        print("Không thể tải hình ảnh.")

def scrape_shopee_product_images(product_url):
    # Tải trang web sản phẩm
    response = requests.get(product_url)
    if response.status_code != 200:
        print("Không thể truy cập trang web.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm tất cả các thẻ <img> có chứa hình ảnh sản phẩm
    img_tags = soup.find_all('img', class_='IMAW1w')
    print(img_tags)
    
    # Tạo thư mục 'images' nếu nó chưa tồn tại
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # Tải và lưu tất cả các hình ảnh sản phẩm
    for idx, img_tag in enumerate(img_tags):
        image_url = img_tag['src']
       
        save_path = os.path.join('images', f'image_{idx}.jpg')
        download_image(image_url, save_path)

def main():
    # Nhập URL của sản phẩm trên Shopee
    product_url = input("Nhập URL của sản phẩm trên Shopee: ")
    
    # Kiểm tra xem URL hợp lệ không
    if "shopee" not in product_url:
        print("URL không hợp lệ.")
        return
    
    # Phân tích trang web và tải tất cả các hình ảnh của sản phẩm
    scrape_shopee_product_images(product_url)

if __name__ == "__main__":
    main()
