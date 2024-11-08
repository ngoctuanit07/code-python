import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import json

# Hàm để lấy thông tin sản phẩm từ link
def crawl_product(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Giả định cấu trúc HTML cụ thể
    product_name = soup.find('h1', class_='product-title').text.strip()
    product_image = soup.find('img', class_='wp-post-image')['src']
    #product_price = soup.find('span', class_='product-price').text.strip().replace('$', '')  # Loại bỏ ký hiệu tiền tệ
    product_description = soup.find('div', class_='woocommerce-Tabs-panel--description').text.strip()  # Lấy mô tả dài
    product_short_description = soup.find('div', class_='product-short-description').text.strip()  # Lấy mô tả ngắn
    return {
        'name': product_name,
        'image': product_image,
        'description': product_description,
        'short_description': product_short_description
    }

# Hàm để import sản phẩm vào WooCommerce qua API
def import_to_woocommerce(product_data, wc_api_url, consumer_key, consumer_secret, category_id):
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        'name': product_data['name'],
        'type': 'simple',
        'description': product_data['description'],  # Thêm mô tả vào payload
        'short_description': product_data['short_description'],  # Thêm mô tả ngắn vào payload
        'categories': [
            {'id': category_id}
        ],
        'images': [
            {
                'src': product_data['image']
            }
        ]
    }

    response = requests.post(
        wc_api_url + '/wp-json/wc/v3/products',
        headers=headers,
        data=json.dumps(payload),
        auth=HTTPBasicAuth(consumer_key, consumer_secret)
    )

    if response.status_code == 201:
        print('Sản phẩm đã được import thành công vào WooCommerce.')
    else:
        print('Lỗi khi import sản phẩm:', response.text)

# Link sản phẩm
product_link = 'https://giadung1.giaodienwebmau.com/robot-hut-bui-va-lau-nha-rapido-rr8/'
wc_api_url = 'https://demothietke.nguyenngoctuan07.com'
consumer_key = 'ck_550535c2ffd671c598d94a70916dd3dc6b365024'
consumer_secret = 'cs_0f281d1f8c3daaf2c20704bf73f75f768eee1820'
category_id = 72  # ID danh mục truyền vào

# Crawl sản phẩm và import vào WooCommerce
product_data = crawl_product(product_link)
import_to_woocommerce(product_data, wc_api_url, consumer_key, consumer_secret, category_id)
