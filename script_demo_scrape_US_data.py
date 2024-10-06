import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def scrape_usa_data_polymarket(url, crawler):
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            content = result.markdown
            
            # Extract total volume
            volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
            total_volume = volume_match.group(1).replace(',', '') if volume_match else "N/A"
            
            # Extract Donald Trump's percentage
            trump_match = re.search(r'Donald Trump\s+(\d+\.\d+)%', content)
            trump_percentage = trump_match.group(1) if trump_match else "N/A"
            
            return total_volume, trump_percentage
        else:
            print(f"Failed to scrape data from: {url}")
            return None, None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None, None

async def main():
    urls = {
        "US": 'https://polymarket.com/event/presidential-election-winner-2024'
    }

    async with AsyncWebCrawler(verbose=True) as crawler:
        results = {}
        for key, value in urls.items():
            print(f"\nScraping data for {key} from: {value}")
            total_volume, trump_percentage = await scrape_usa_data_polymarket(value, crawler)
            if total_volume and trump_percentage:
                print(f"US Total Amount\t{total_volume}")
                print(f"US Repbl. Odds\t{trump_percentage}")
                results[key] = (total_volume, trump_percentage)
            else:
                print(f"Failed to scrape data for {key} from: {value}")

if __name__ == "__main__":
    asyncio.run(main())