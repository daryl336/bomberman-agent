import os
import pickle
import uuid
import logging
import json
import uvicorn
import traceback
from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()

from agents import set_tracing_disabled
set_tracing_disabled(True)

from app import bot
from agentic_app import agentic_bot

app = FastAPI()

@app.post("/")
async def generate_action(request: Request):
    logging.info('Processing a request.')
    data = await request.json()
    need_reasoning = data.get("need_reasoning","no")
    game_state = data.get("game_state","{}")
    valid_movement = data.get("valid_movement","[]")
    nearest_crate = data.get("nearest_crate","{}")
    check_bomb_radius = data.get("check_bomb_radius","{}")
    plant_bomb_available = data.get("plant_bomb_available","{}")
    coins_collection_policy = data.get("coins_collection_policy","{}")
    movement_history = data.get("movement_history","[]")
    if isinstance(valid_movement, str):
        valid_movement = json.loads(valid_movement)
    if isinstance(nearest_crate, str):
        nearest_crate = json.loads(nearest_crate)
    if isinstance(check_bomb_radius, str):
        check_bomb_radius = json.loads(check_bomb_radius)
    if isinstance(plant_bomb_available, str):
        plant_bomb_available = json.loads(plant_bomb_available)
    if isinstance(coins_collection_policy, str):
        coins_collection_policy = json.loads(coins_collection_policy)
    if isinstance(movement_history, str):
        movement_history = json.loads(movement_history)
    try:
        # Bot Response in the final answer already, together with the final map dict url.
        final_answer = await bot(need_reasoning, game_state, valid_movement, nearest_crate, check_bomb_radius, plant_bomb_available, coins_collection_policy, movement_history)
        return final_answer
    except Exception as e:
        print(f"Error : {str(e)}")
        print(traceback.format_exc())
        return {"reasoning": f"Error! {str(e)}", "action":"WAIT"}

@app.post("/agentic-predict")
async def generate_action_agentic(request: Request):
    logging.info('Processing a request for agentic prediction.')
    data = await request.json()
    need_reasoning = data.get("need_reasoning","no")
    game_state = data.get("game_state","{}")
    valid_movement = data.get("valid_movement","[]")
    nearest_crate = data.get("nearest_crate","{}")
    check_bomb_radius = data.get("check_bomb_radius","{}")
    plant_bomb_available = data.get("plant_bomb_available","{}")
    coins_collection_policy = data.get("coins_collection_policy","{}")
    movement_history = data.get("movement_history","[]")
    opponents = data.get("opponents","[]")
    if isinstance(valid_movement, str):
        valid_movement = json.loads(valid_movement)
    if isinstance(nearest_crate, str):
        nearest_crate = json.loads(nearest_crate)
    if isinstance(check_bomb_radius, str):
        check_bomb_radius = json.loads(check_bomb_radius)
    if isinstance(plant_bomb_available, str):
        plant_bomb_available = json.loads(plant_bomb_available)
    if isinstance(coins_collection_policy, str):
        coins_collection_policy = json.loads(coins_collection_policy)
    if isinstance(movement_history, str):
        movement_history = json.loads(movement_history)
    if isinstance(opponents, str):
        opponents = json.loads(opponents)
    try:
        # Agentic bot: Uses PredictAgent tools to predict each opponent's move, then makes final decision
        final_answer = await agentic_bot(need_reasoning, game_state, valid_movement, nearest_crate, check_bomb_radius, plant_bomb_available, coins_collection_policy, movement_history, opponents)
        return final_answer
    except Exception as e:
        print(f"Error : {str(e)}")
        print(traceback.format_exc())
        return {"reasoning": f"Error! {str(e)}", "action":"WAIT"}


if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=6000, reload=True, proxy_headers=True)
