import scrapy


class VisionsSpider(scrapy.Spider):
    name = "visionsSpider"
    allowed_domains = ["visions.ca"]

    def start_requests(self):
        # start_urls = ["http://www.visions.ca/default.aspx"]
        default_url = 'http://www.visions.ca/default.aspx'
        # item_test_url = 'http://www.visions.ca/Catalogue/Category/Default.aspx?categoryId=598&menu=502'
        yield scrapy.Request(url=default_url, callback=self.parse)
        # yield scrapy.Request(url=item_test_url, callback=self.parse_first_item)

    def parse(self, response):
        """ default parse method"""
        # insert contains for last categories
        for menu_item in response.xpath('//li[contains(@class, "menulevel-0")]'):
            next_page = menu_item.css('a::attr(href)').extract_first()
            # the last item has an empty link
            if next_page[0] == "/":
                next_page = response.urljoin(next_page)
                menu_item = menu_item.xpath('./a/span/text()').extract_first()
                self.log('Department: ' + menu_item)
                yield scrapy.Request(next_page, callback=self.parse_category)
        # break

    def parse_category(self, response):
        # self.log("here")
        # if response.xpath('//td[@class="leftPanel"]').extract_first is not None:
        for category in response.xpath('//td[@class="leftPanel"]'
                                       '/div[@id="subcatemenu-container"]/div/ul/li'):
            next_page = category.css('a::attr(href)').extract_first()
            next_page = response.urljoin(next_page)
            category = category.xpath('./a/text()').extract_first()
            if category and next_page is not None:
                self.log("category: " + category)
                yield scrapy.Request(next_page, callback=self.parse_sub_category)
        # break

    def parse_sub_category(self, response):
        # self.log("subCat")
        for sub_category in response.xpath(
                '//td[@class="leftPanel"]/div/div/ul[@class="subcatemenu-items"]'
                '/li'):
            sub_category = sub_category.xpath('./div/div[@class="itembox-name"]'
                                            '/a/text()').extract_first()
            if sub_category is not None:
                self.log("sub_category: " + sub_category)
        # break

    def parse_first_item(self, response):
        """ parses only the first item
            not using Items
            'qty': response.xpath().extract_first()"""
        yield {
            'title': response.xpath('//div[@class="productItemMain"]'
                                    '/div[@class="productName"]/a/text()')
                                    .extract_first().strip(),
            'price': response.xpath('//div[@class="productItemMain"]'
                                    '/div[@class="skuPriceAirMiles"]/span[@class="price"]/text()')
                                    .extract_first().strip()
        }
