BOT_NAME = 'myproject'

SPIDER_MODULES = ['myproject.spiders']
NEWSPIDER_MODULE = 'myproject.spiders'
FEED_URI = "data.csv"
ITEM_PIPELINES = {
  'myproject.pipelines.MyPipeline': 300,
}