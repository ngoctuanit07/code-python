import requests
from bs4 import BeautifulSoup

from datetime import datetime

url = "https://taphoahaanh.net"

def check_seo(url):

  errors = []

  # Lấy nội dung HTML
  response = requests.get(url)
  html = response.text

  # Phân tích HTML
  soup = BeautifulSoup(html, "html.parser")

  # Kiểm tra tiêu đề trang
  page_title = soup.title.text
  if not page_title or len(page_title) > 60:
    errors.append("Tiêu đề trang không hợp lệ")

  # Kiểm tra mô tả trang
  page_description = soup.find("meta", {"name":"description"})
  if not page_description or len(page_description["content"]) > 160: 
    errors.append("Mô tả trang không hợp lệ")

  # Kiểm tra heading tags
  h1_count = len(soup.find_all("h1"))
  if h1_count != 1:
    errors.append(f"Có {h1_count} thẻ h1, cần chỉ có 1")

  # Kiểm tra tốc độ load trang
  response_time = response.elapsed.total_seconds()
  if response_time > 3:
    errors.append(f"Thời gian load trang {response_time} giây - cần nhanh hơn")

  # Kiểm tra sitemap
  sitemap = soup.find("loc", {"text": "/sitemap.xml"})
  if not sitemap:
    errors.append("Không tìm thấy sitemap")  

  # Kiểm tra từ khóa trong meta keywords
  keywords = soup.find("meta", {"name":"keywords"})
  if not keywords or len(keywords["content"].split(",")) < 5:
    errors.append("Meta keywords không hợp lệ")

  # Kiểm tra alt text hình ảnh
  images = soup.find_all("img")
  for image in images:
    if not image.has_attr("alt") or not image["alt"]:
      errors.append(f"Hình ảnh {image['src']} thiếu alt text")

  

  return errors

errors = check_seo(url)

# Xuất ra file txt các lỗi tìm thấy  
with open("seo_errors.txt", "w") as f:
  for error in errors:
    f.write(error + "\n")

print("Đã kiểm tra và xuất kết quả ra seo_errors.txt")