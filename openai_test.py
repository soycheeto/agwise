from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()
client = OpenAI(
    base_url=getenv("OPENROUTER_BASE_URL"),
    api_key=getenv("OPENROUTER_API_KEY"),
)

model = "openai/gpt-3.5-turbo"

# Non-streaming:
print("----- standard request -----")
completion = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(completion.choices[0].message.content)