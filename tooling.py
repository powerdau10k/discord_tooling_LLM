import os
import dotenv
from googleapiclient.discovery import build
from py_expression_eval import Parser
from groq import Groq
from wolframalpha import Client
import re
import wolframalpha
import asyncio
from simpletest import scrape_query
from searchpro import answer_question
class Groq_Agent:
    def __init__(self):
        dotenv.load_dotenv()
        prompt_file = open("sysprompts/prompt3.txt", "r")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.google_cse_api_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.wolfram_app_id = os.getenv("WOLFRAM_APP_ID")
        self.model = "llama-3.1-70b-versatile"
        self.System_prompt = prompt_file.read()

        self.wolfram_client = wolframalpha.Client(self.wolfram_app_id)
        self.client = Groq(api_key=self.groq_api_key)
        self.parser = Parser()

    async def wolfram_alpha(self, prompt):
        res = await self.wolfram_client.aquery(prompt)
        return res

    async def search(self, search_term):
        return await answer_question(search_term)


#    async def search(self, search_term):
 #       search_result = ""
  #      service = build("customsearch", "v1", developerKey=self.google_cse_api_key)
   #     res = service.cse().list(q=search_term, cx=self.google_cse_id, num=10).execute()
    #    for result in res["items"]:
     #       search_result_snippets = search_result + result["snippet"]
      #  scrapes = await scrape_query(search_term)
       # print(scrapes)
        #return str(scrapes)

    async def calculator(self, str):
        return self.parser.parse(str).evaluate({})

    async def rethink(self, thought):
        return thought

    async def stream_agent(self, prompt):
        return_message = []
        messages = [
            {"role": "system", "content": self.System_prompt},
            {"role": "user", "content": prompt},
        ]

        def extract_action_and_input(text):
            action_pattern = r"Action: (.+?)\n"
            input_pattern = r"Action Input: \"(.+?)\""
            action = re.findall(action_pattern, text)
            action_input = re.findall(input_pattern, text)
            return action, action_input

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=4000,
                top_p=0.1,
            )
            response_text = response.choices[0].message.content
            return_message.append(response_text)
            action, action_input = extract_action_and_input(response_text)
            if action:
                if action[-1] == "Response To Human":
                    if action_input:
                        response_to_human = f"\nResponse to Human:\n{action_input[-1]}"
                    else:
                        response_to_human = (
                            "\nResponse to Human:\nNo response available."
                        )
                    return_message.append(response_to_human)
                    print(return_message)
                    break  # Exit the loop immediately after responding
                else:
                    # Process other tools if it's not a "Response To Human"
                    if action[-1] == "Search":
                        tool = self.search
                    elif action[-1] == "Calculator":
                        tool = self.calculator
                    elif action[-1] == "WolframAlpha":
                        tool = self.wolfram_alpha
                    elif action[-1] == "Rethink":
                        tool = self.rethink

                    if action_input:
                        observation = await tool(action_input[-1])
                    else:
                        observation = await self.rethink(return_message)

                    observation = str(observation)
                    print(observation)
                    messages.extend([
                        {"role": "assistant", "content": response_text},
                        {"role": "user", "content": observation},
                    ])
            else:
                break
        return return_message


async def main():
    agent = Groq_Agent()
    result = await agent.stream_agent(prompt="tell me about yesterday's biggest news")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
