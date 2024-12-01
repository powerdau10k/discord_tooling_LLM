import asyncio
import aiohttp
import os 
import dotenv
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def extract_hyperlinks(cse_response):
    items = cse_response.get('items', [])
    links = [item['link'] for item in items if 'link' in item]
    return links

async def return_cse_response(query):
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
    service = build("customsearch", "v1", developerKey=google_cse_api_key)
    res = service.cse().list(q=query, cx=google_cse_id, num=3).execute()
    return res


async def scrape_links(url):
    try:
        async with aiohttp.ClientSession() as session:
            jina_url = "https://r.jina.ai/" + url 
            async with session.get(jina_url, headers=headers) as response:
                response.raise_for_status()
                print(f"Successfully fetched {jina_url}")
                return await response.text()
    except aiohttp.ClientError as e:
        print(f"Client error occurred while fetching {jina_url}: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"Request timed out for {jina_url}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching {jina_url}: {e}")
        return None

async def scrape_query(query):
    cse_response = await return_cse_response(query)
    hyperlinks = extract_hyperlinks(cse_response)
    scrapes = []
    for url in hyperlinks:
        try:
            markdown = await scrape_links(url)
            scrapes.append(markdown)
        except Exception as e:
            print(f"An error occurred with jina-ai while processing {url}: {e}")
            continue
    return scrapes


async def main():
    query = "What is the capital of France?"
    results = await scrape_google(query)
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
