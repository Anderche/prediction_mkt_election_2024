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
            
            # Extract total volume
            volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
            total_volume = float(volume_match.group(1).replace(',', '')) if volume_match else None
            
            # Extract Republican percentage
            republican_match = re.search(r'Republican.*?(\d+\.?\d*)%', content, re.DOTALL)
            republican_percentage = float(republican_match.group(1)) if republican_match else None
            
            # Extract Democrat percentage
            democrat_match = re.search(r'Democrat.*?(\d+\.?\d*)%', content, re.DOTALL)
            democrat_percentage = float(democrat_match.group(1)) if democrat_match else None
            
            return {
                'total_volume': total_volume,
                'republican_percentage': republican_percentage,
                'democrat_percentage': democrat_percentage
            }
        else:
            print(f"Failed to scrape data from: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

async def main():
    urls = {
        # "Florida": "https://polymarket.com/event/florida-presidential-election-winner",
        "California": "https://polymarket.com/event/california-presidential-election-winner",
    }

    async with AsyncWebCrawler(verbose=True) as crawler:
        results = {}
        for state, url in urls.items():
            print(f"\nScraping data for {state} from: {url}")
            content = await scrape_polymarket(url, crawler)
            if content:
                print(f"Scraped content for {state}:")
                print(f"Total Volume: {content['total_volume']:,.2f}")
                print(f"Republican Percentage: {content['republican_percentage']:.1f}")
                print(f"Democrat Percentage: {content['democrat_percentage']:.1f}")
                results[state] = content
            else:
                print(f"Failed to scrape data for {state} from: {url}")
        
        print("\nFinal Results:")
        for state, data in results.items():
            print(f"{state}:")
            print(f"Total Volume: ${data['total_volume']:,.2f}")
            print(f"Republican Percentage: {data['republican_percentage']:.1f}%")
            print(f"Democrat Percentage: {data['democrat_percentage']:.1f}%")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
