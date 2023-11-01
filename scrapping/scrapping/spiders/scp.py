import scrapy
import logging
import re

class ScpSpider(scrapy.Spider):
    name = "scp"

    # Url a ser raspada
    start_urls = ['https://www.mercadolivre.com.br/ofertas#c_id=/home/promotions-recommendations&c_uid=b3207326-09f2-403a-a741-48fdb2d5fbd8']

    def parse(self, response, **kwargs):
        # Itera sobre os elementos HTML que contêm as informações dos produtos
        for i in response.xpath('//li[contains(@class, "promotion-item")]/div'):
            # Obtém os elementos de preço (atual e anterior)
            price_elements = i.xpath('.//span[@class="andes-money-amount__fraction"]/text()').getall()

            if len(price_elements) >= 2:
                # Obter preço atual e preço anterior
                current_price_txt = price_elements[0]
                previous_price_txt = price_elements[1]

            else:
                current_price = ''
                previous_price = ''

            # Obtém o título e o link do produto
            title = i.xpath('.//p[@class="promotion-item__title"]/text()').get()
            link = i.xpath('.//a[@class="promotion-item__link-container"]/@href').get()
            discount = i.xpath('.//span[@class="andes-money-amount__discount"]/text()').re_first(r'\d+')
            url_image = i.xpath('//div[@class="promotion-item__img-container"]/img/@src').get()

            current_price = re.sub(r'[^0-9]', '', current_price_txt)
            previous_price = re.sub(r'[^0-9]', '', previous_price_txt)

            if current_price and previous_price and title and link and discount and url_image:
                yield {
                    'title': title,
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'discount' : discount,
                    'link': link,
                    'url_image' : url_image
                }
            else:
                self.logger.warning("Element not found: current_price={}, title={}, link={}".format(current_price, title, link))

        # Percorre todas as páginas de resultados
        next_page = response.xpath('//a[contains(@title,"Próxima")]/@href').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
        else:
            self.logger.warning("No 'Próxima' link found.")

logging.getLogger('scrapy').setLevel(logging.WARNING)
