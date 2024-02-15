import csv

class MyPipeline(object):
  def process_item(self, item, spider):
    # Lưu trữ dữ liệu vào file CSV
    with open("data.csv", "a", newline="") as f:
      writer = csv.writer(f)
      writer.writerow([item["title"], item["content"]])

    return item