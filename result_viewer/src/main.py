from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/graph")
def graph_index():
  # Read all file basenames in the "graphs" directory
  graphs = os.listdir("./graphs")
  # Return the list of file basenames
  graphs = [f for f in graphs if os.path.isfile(os.path.join("./graphs", f))]
  return graphs


@app.get("/graph/{graph_name}")
def graph(graph_name: str):
  # Read the file content from the "graphs" directory and returns as json
  with open(f"./graphs/{graph_name}") as f:
    return json.load(f)