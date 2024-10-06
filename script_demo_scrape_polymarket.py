import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def scrape_polymarket(url, crawler):
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            content = result.markdown
            
            # Extract total volume and convert to float
            volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
            total_volume = float(volume_match.group(1).replace(',', '')) if volume_match else 0.0
            
            # Extract Republican percentage and convert to float
            republican_match = re.search(r'Republican.*?\n.*?\n([0-9.]+)%', content, re.DOTALL)
            republican_percentage = float(republican_match.group(1)) if republican_match else 0.0
            
            # Return only numerical values without special characters
            return f"{total_volume:.2f}\n{republican_percentage:.1f}"
        else:
            print(f"Failed to scrape data from: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

async def main():

    urls = {
        "Georgia": "https://polymarket.com/event/georgia-presidential-election-winner",
        "Arizona": "https://polymarket.com/event/arizona-presidential-election-winner",
        "Wisconsin": "https://polymarket.com/event/wisconsin-presidential-election-winner",
        "Pennsylvania": "https://polymarket.com/event/pennsylvania-presidential-election-winner",
        "North Carolina": "https://polymarket.com/event/north-carolina-presidential-election-winner",
        "Nevada": "https://polymarket.com/event/nevada-presidential-election-winner",
        "Michigan": "https://polymarket.com/event/michigan-presidential-election-winner"
    }

    async with AsyncWebCrawler(verbose=True) as crawler:
        results = {}
        for state, url in urls.items():
            print(f"\nScraping data for {state} from: {url}")
            content = await scrape_polymarket(url, crawler)
            if content:
                print(f"Scraped content for {state}:")
                print(content)
                results[state] = content
            else:
                print(f"Failed to scrape data for {state} from: {url}")
        
        print("\nFinal Results:")
        for state, data in results.items():
            print(f"{state}:")
            print(data)

if __name__ == "__main__":
    asyncio.run(main())
