import os
import dotenv
import discord
from responses import get_answer, get_tool
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# bot setup
intents = discord.Intents(messages=True, guilds=True)
intents.message_content = True
client = discord.Client(intents=intents)


# message func
async def send_message(message, user_message):
    if not user_message:
        print("empty user_message")
        return

    def split_message(text, max_length=2000):
        """
        Splits text into chunks of max_length or less,
        using newline characters as split points if possible.
        """
        chunks = []
        while len(text) > max_length:
            # Find the last newline character within the max_length limit
            split_pos = text.rfind("\n", 0, max_length)
            if split_pos == -1:  # No newline found, split at max_length
                split_pos = max_length
            chunks.append(text[:split_pos].strip())
            text = text[split_pos:].lstrip()
        if text:
            chunks.append(text.strip())
        return chunks

    if user_message[0] == "?":
        user_message = user_message[1:]
        response = get_answer(user_message)
        # Split response if necessary and send it
        for chunk in split_message(response):
            await message.author.send(chunk)
        return

    elif user_message[0] == "!":
        user_message = user_message[1:]
        response = await get_tool(user_message)
        del response[-1]  # Remove redundant "Response to Human:"
        for item in response:
            # Split each item if necessary and send it
            for chunk in split_message(item):
                await message.channel.send(chunk)
        return

    else:
        response = get_answer(user_message)
        # Split response if necessary and send it
        for chunk in split_message(response):
            await message.channel.send(chunk)


# bot startup
@client.event
async def on_ready():
    print(f"{client.user} is now running")


# message handling
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f"{username} said: '{user_message}' ({channel})")
    await send_message(message, user_message)


def main():
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
