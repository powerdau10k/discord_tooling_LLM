#setting up gemini flash
import os
import dotenv
import google.generativeai as genai


class Geminiflash:
    def __init__(self,sysprompt):
        dotenv.load_dotenv()
        self.jina_url = 'https://r.jina.ai/'
        with open(f"sysprompts/{sysprompt}.txt", "r") as f:
            self.sysprompt = f.read()
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", system_instruction=self.sysprompt
        )

    def generate_response(self, jina_scrape):
        response = self.model.generate_content(jina_scrape)
        return response.text


### setting up cleanscraper
import os
import dotenv
import aiohttp
import google.generativeai as genai
import asyncio


class Cleanscraper:
    def __init__(self):
        dotenv.load_dotenv()
        self.jina_url = 'https://r.jina.ai/'
        with open("sysprompts/sysprompt_summary.txt", "r") as f:
            self.sysprompt_summary = f.read()
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=self.gemini_api_key)
        self.summary_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", system_instruction=self.sysprompt_summary
        )


    async def simple_scrape(self, url):
        whole_url = self.jina_url + url
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(whole_url) as response:
                    return await response.text()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def summarize_and_extract(self, jina_scrape):
        summary = self.summary_model.generate_content(jina_scrape)
        return summary.text
    
async def clean_scrape(scraper,url):
    jina_scrape = await scraper.simple_scrape(url)
    summary = scraper.summarize_and_extract(jina_scrape)
    return summary


####using clean scraper to answer question 
import google.generativeai as genai
from googleapiclient.discovery import build
import asyncio
import os

def final_response(question,summaries,promptname):     
    gemflash =  Geminiflash("final_answer")
    response = gemflash.generate_response(str(summaries))
    return response


async def get_facts(question):
    summaries = []
    scraper = Cleanscraper()
    query = formulate_response(question,"question2query")
    links = return_links(query)
    for link in links:
        jina_scrape = await scraper.simple_scrape(link)
        summary = scraper.summarize_and_extract(jina_scrape)
        summ_dict = {"link": link, "summary": summary}
        summaries.append(summ_dict)
    return summaries


def formulate_response(LLMInput,promptname):
    gemflash = Geminiflash(promptname)
    response = gemflash.generate_response(LLMInput)
    return response


def return_links(query):
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
    service = build("customsearch", "v1", developerKey=google_cse_api_key)
    res = service.cse().list(q=query, cx=google_cse_id, num=5).execute()
    links = extract_hyperlinks(res)
    return links

def extract_hyperlinks(cse_response):
    items = cse_response.get("items", [])
    links = [item["link"] for item in items if "link" in item]
    return links

async def answer_question(question):
    summaries = await get_facts(question)
    response = final_response(question,summaries,"final_answer")
    return response









