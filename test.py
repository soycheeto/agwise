import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
import requests
import re
import pandas as pd

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("Missing or empty PERPLEXITY_API_KEY environment variable")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "accept": "application/json",
}

def perplexity_query(messages):
    url = "https://api.perplexity.ai/chat/completions"
    json_data = {
        "model": "sonar-reasoning",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 100,  # Reduced token limit for concise output
    }
    response = requests.post(url, headers=headers, json=json_data, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

# Load sensor data from CSV
df = pd.read_csv("sensor_data.csv", parse_dates=["timestamp"])

print("Preview of 5 entries in sensor_data.csv:")
print(df.head())

class State(TypedDict):
    question: str
    data_summary: str
    answer: str

def generate_data_summary(state: State) -> State:
    recent = df[df["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=1)]
    soil_moisture_avg = recent["soil_moisture"].mean()
    temperature_avg = recent["temperature"].mean()
    humidity_avg = recent["humidity"].mean()
    summary = (
        f"Average soil moisture: {soil_moisture_avg:.1f}%, "
        f"temperature: {temperature_avg:.1f}°C, "
        f"humidity: {humidity_avg:.1f}%."
    )
    state["data_summary"] = summary
    return state

def generate_decision(state: State) -> State:
    prompt = (
        "Provide a clear, direct irrigation recommendation in exactly one sentence to the farmer. "
        "Do NOT provide explanations, uncertainty, or hedging. "
        "Respond only with the one sentence.\n\n"
        f"Sensor data summary: {state['data_summary']}\n"
        f"Question: {state['question']}\n"
        "Irrigation recommendation:"
    )
    messages = [
        {"role": "system", "content": "You are an expert agronomist."},
        {"role": "user", "content": prompt}
    ]
    answer = perplexity_query(messages)
    # Extract first sentence, remove trailing tokens like '<think>'
    first_sentence = re.split(r'[.\n<]', answer.strip())[0].strip()
    if not first_sentence.endswith('.'):
        first_sentence += '.'
    state["answer"] = first_sentence
    return state

graph = StateGraph(State)
graph.add_node("generate_summary", generate_data_summary)
graph.add_node("generate_decision", generate_decision)
graph.add_edge(START, "generate_summary")
graph.add_edge("generate_summary", "generate_decision")
graph.add_edge("generate_decision", END)

agent = graph.compile()

initial_state = {
    "question": "Should I irrigate my crop field today based on current soil moisture and weather?",
    "data_summary": "",
    "answer": "",
}

result_state = agent.invoke(initial_state)
print(f"Final decision/answer: {result_state['answer']}")
