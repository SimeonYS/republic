import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import RepublicItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class RepublicSpider(scrapy.Spider):
	name = 'republic'
	start_urls = ['https://www.firstrepublic.com/about-us/newsroom?gnav=globalheader;aboutus-news']

	def parse(self, response):
		post_links = response.xpath('//td/a/@href').getall()
		post_links = [link for link in post_links if not "pdf" in link ]
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="page-heading--description"]/text()').get()
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('(//div[@class="newsroom-detail"]/div)[2]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=RepublicItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
