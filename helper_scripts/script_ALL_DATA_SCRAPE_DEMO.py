import asyncio
from crawl4ai import AsyncWebCrawler
import re

def extract_party_data(content, party):
    pattern = rf"{party}\s*\n\s*\$([\d,]+)\s*Vol\.\s*\n\s*([\d.]+)%"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        volume = match.group(1).replace(',', '')
        percentage = match.group(2)
        return (party, int(volume), float(percentage))
    return None

async def scrape_polymarket(url, crawler):
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            return result.markdown
        else:
            print(f"Failed to scrape data from: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

async def main():

    urls = {
        "US": "https://polymarket.com/event/presidential-election-winner-2024",
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
            content = await scrape_polymarket(url, crawler)
            if content:
                republican_data = extract_party_data(content, "Republican")
                democratic_data = extract_party_data(content, "Democrat")
                results[state] = {
                    "Republican": republican_data,
                    "Democrat": democratic_data
                }
            else:
                print(f"Failed to scrape data for {state} from: {url}")
        
        for state, data in results.items():
            print(f"{state}:")
            print(f"Republican: {data['Republican']}")
            print(f"Democrat: {data['Democrat']}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
