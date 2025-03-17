import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from playwright.async_api import async_playwright


class IncidentHistorySpider(scrapy.Spider):
    name = "incident_history"
    # start_urls = ["data:,"]  # avoid using the default Scrapy downloader

    async def parse(self, response):
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()
            await page.goto("https://status.digitalocean.com/history")
            title = await page.title()
            print(page)
            return {"title": title}


process = CrawlerProcess(settings=get_project_settings())

process.crawl(IncidentHistorySpider)
process.start()
