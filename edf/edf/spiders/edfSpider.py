import scrapy
from scrapy import Spider
from scrapy.selector import Selector
from edf.items import EdfItem
import html2text

from scrapy.http import HtmlResponse

class EdfSpider(Spider):
	name="edf"
	allowed_domains = []

	start_urls = ["https://forum.quechoisir.org/edf-f400.html",
				  "https://forum.quechoisir.org/edf-f400-25.html",
				  "https://forum.quechoisir.org/edf-f400-50.html",
				  "https://forum.quechoisir.org/edf-f400-75.html",
				  "https://forum.quechoisir.org/edf-f400-100.html"]

	def parse(self, response):
		hxs = Selector(response)
		for href in hxs.xpath('//h2[@class="ufc-title"]/a/@href').extract():
			if href is not None:
				child_page = response.urljoin(href)
				yield scrapy.Request(child_page, callback=self.parse_posts)

	def parse_posts(self, response):
		self.log("parsing posts: %s" % response.url)

		try:
			hxs = Selector(response)
			item = EdfItem()

			r = hxs.xpath('//div[@class="content"]/text()').extract()
			title = hxs.xpath('//h2[@class="first"]/a/text()').extract()

			item['title'] = title
			for line in r:
				item['post'] = line

				yield item

		except AttributeError:
			self.log('No data to extract from : %s' % response.url)

		next_page = hxs.xpath('//div[@class="pagination"]/ul//li[@class="next"]//@href').extract_first()
		if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse_posts)
