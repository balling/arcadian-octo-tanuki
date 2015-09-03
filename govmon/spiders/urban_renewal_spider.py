from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from govmon.items import UrbanRenewalItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

file_extension = [
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',
    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp',

    # other
    'pdf', 'zip', 'rar',
]


class URASpider(CrawlSpider):
    name = 'ura'
    allowed_domains = ['ura.org.hk']
    start_urls = [
        'http://www.ura.org.hk/en/sitemaps.aspx'
    ]

    rules = (
        Rule(LinkExtractor(allow='\.aspx', allow_domains=allowed_domains), callback='print_url', follow=True),
    )

    def print_url(self, response):
        """
            @url http://www.ura.org.hk/en/schemes-and-policies/redevelopment/ura-implemented-projects/reimbursement.aspx
            @returns items 1 1
            @returns requests 0 0
            @scrapes title link html text last_updated file_urls
        """
        l = ItemLoader(item=UrbanRenewalItem(), response=response)
        l.add_xpath('title', '//title')
        l.add_value('link', response.url)
        l.add_xpath('text', '//div[@id="content"]')
        l.add_xpath('html', '/html')
        l.add_xpath('last_updated', '//div[@class="lastUpdated"]')
        lx = LinkExtractor(allow=['\.' + ext for ext in file_extension],
                           deny_extensions=())
        l.add_value('file_urls', [link.url for link in lx.extract_links(response)])
        return l.load_item()


if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(URASpider)
    process.start()
