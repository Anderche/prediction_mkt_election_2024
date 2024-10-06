import asyncio
from crawl4ai import AsyncWebCrawler

async def scrape_full_page(url, crawler):
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            print(f"Successfully scraped data from: {url}")
            print("\nFull page content:")
            print(result.markdown)
            return result.markdown
        else:
            print(f"Failed to scrape data from: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

async def main():
    # Example URL to scrape (you can change this to any URL you want to scrape)
    url = "https://polymarket.com/event/presidential-election-winner-2024"

    async with AsyncWebCrawler(verbose=True) as crawler:
        print(f"Scraping full page content from: {url}")
        content = await scrape_full_page(url, crawler)
        
        if content:
            print("\nScraping completed successfully.")
        else:
            print("\nFailed to scrape the page.")

if __name__ == "__main__":
    asyncio.run(main())