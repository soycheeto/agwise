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
        "max_tokens": 500,
    }
    response = requests.post(url, headers=headers, json=json_data, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
df = pd.read_csv("sensor_data.csv", parse_dates=["timestamp"])
print("Preview of 5 entries in sensor_data.csv:")
print(df.head())
class State(TypedDict):
    question: str
    data_summary: str  # Replace query with summarized data string
    result: str
    answer: str
def generate_data_summary(state: State) -> State:
    recent = df[df["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=1)]
    soil_moisture_avg = recent["soil_moisture"].mean()
    temp_avg = recent["temperature"].mean()
    humidity_avg = recent["humidity"].mean()
    summary = (
        f"Recent soil moisture average: {soil_moisture_avg:.2f}, "
        f"temperature average: {temp_avg:.1f}C, "
        f"humidity average: {humidity_avg:.1f}%."
    )
    state["data_summary"] = summary
    return state
def run_dummy_query(state: State) -> State:
    state["result"] = state.get("data_summary", "")
    return state
def generate_decision(state: State) -> State:
    messages = [
        {"role": "system", "content": "Based on sensor data summary and question, provide an agricultural decision or answer."},
        {"role": "user", "content": f"Sensor data summary: {state['data_summary']}\nQuestion: {state['question']}"}
    ]
    answer = perplexity_query(messages)
    state["answer"] = answer
    return state
graph = StateGraph(State)
graph.add_node("generate_data_summary", generate_data_summary)
graph.add_node("dummy_query", run_dummy_query)
graph.add_node("generate_decision", generate_decision)
graph.add_edge(START, "generate_data_summary")
graph.add_edge("generate_data_summary", "dummy_query")
graph.add_edge("dummy_query", "generate_decision")
graph.add_edge("generate_decision", END)
agent = graph.compile()
initial_state = {
    "question": "Should I irrigate my crop field today based on current soil moisture and weather?",
    "data_summary": "",
    "result": "",
    "answer": "",
}
result_state = agent.invoke(initial_state)
print(f"Final decision/answer: {result_state['answer']}")
