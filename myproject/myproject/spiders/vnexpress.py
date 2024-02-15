import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class VnExpressSpider(CrawlSpider):
  name = 'vnexpress'
  allowed_domains = ["vnexpress.net"]
  start_urls = ["https://vnexpress.net/"]

  rules = (
    Rule(LinkExtractor(allow=r"/\d+/\d+/\d+/\w+-\d+.html"), callback="parse_item"),
    Rule(LinkExtractor(allow=r"/\d+/\d+/\w+-\d+.html"), callback="parse_item"),
  )

  def parse_item(self, response):
    # Lấy dữ liệu từ trang web
    print(response)
    title = response.css(".title-detail h1::text").get()
    content = response.css(".fck_detail::text").getall()

    # Tạo item
    item = NewsItem()
    item["title"] = title
    item["content"] = content

    # Yield item
    yield item