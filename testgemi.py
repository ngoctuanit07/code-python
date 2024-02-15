import requests
from bs4 import BeautifulSoup

def get_all_links(url):
  """
  Lấy tất cả các liên kết trong URL và xuất ra file txt.

  Args:
    url: URL của trang web bạn muốn lấy liên kết.

  Returns:
    None.
  """

  # Gửi yêu cầu GET đến URL
  response = requests.get(url)

  # Kiểm tra trạng thái HTTP
  if response.status_code == 200:
    # Parse nội dung HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # Tìm tất cả các thẻ <a>
    links = soup.find_all("a")

    # Tạo tập hợp để lưu trữ các liên kết
    links_set = set()

    # Ghi các liên kết vào tập hợp
    for link in links:
      href = link.get("href")
      if href is not None:
        links_set.add(href)

    # Mở file txt để ghi
    with open("links.txt", "w") as f:
      # Ghi từng liên kết vào file txt
      for link in links_set:
        f.write(link + "\n")

  else:
    print(f"Lỗi HTTP: {response.status_code}")

if __name__ == "__main__":
  # URL ví dụ
  url = "https://maytinh7.giaodienwebmau.com/"

  # Lấy tất cả các liên kết trong URL
  get_all_links(url)

  print("Đã xuất tất cả các liên kết không trùng lặp vào file links.txt")