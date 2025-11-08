import os
import json
import asyncio
from typing import List, Dict, Any
from specialised_agents.bomberman import BombermanAgent
from specialised_agents.predict import PredictAgent
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from llm import a_client, a_client_reasoning, a_client_eu2_prod
from agent_settings import MyAgentSettings
from tool_logger import ToolLogger

async def agentic_bot(need_reasoning, game_state, valid_movement, nearest_crate, check_bomb_radius,
                     plant_bomb_available, coins_collection_policy, movement_history, opponents):
    """
    Agentic bot that uses PredictAgent as tools to predict each opponent's move,
    then makes a final decision using the main orchestrator agent.
    """

    # Parse opponent data
    opponent_predictions = {}

    # Step 1: For each opponent, create a PredictAgent and predict their next move
    if opponents and len(opponents) > 0:
        predict_tasks = []
        for opp in opponents:
            opp_name = opp.get("name", "Unknown")
            predict_tasks.append(predict_opponent_move(need_reasoning, opp, game_state, valid_movement, check_bomb_radius, plant_bomb_available))

        # Run all predictions in parallel
        predictions = await asyncio.gather(*predict_tasks, return_exceptions=True)

        for idx, opp in enumerate(opponents):
            opp_name = opp.get("name", "Unknown")
            if idx < len(predictions) and not isinstance(predictions[idx], Exception):
                opponent_predictions[opp_name] = predictions[idx]
            else:
                opponent_predictions[opp_name] = {"action": "UNKNOWN", "reasoning": "Prediction failed"}

    # Step 2: Build input for main orchestrator
    crate_available = nearest_crate.get("crate_available")
    crate_action = nearest_crate.get("crate_action")
    crate_distance = nearest_crate.get("crate_distance")
    crate_reason = nearest_crate.get("crate_reason")
    in_bomb_radius = check_bomb_radius.get("in_bomb_radius")
    in_danger = check_bomb_radius.get("in_danger")
    escape_bomb_action = check_bomb_radius.get("escape_bomb_action")
    plant_bomb = plant_bomb_available.get("plant")
    plant_bomb_reason = plant_bomb_available.get("reason")
    current_status = plant_bomb_available.get("current_status")
    coin_available = coins_collection_policy.get("coin_available")
    coin_action = coins_collection_policy.get("coin_action")
    coin_reason = coins_collection_policy.get("coin_reason")

    current_input = f"Valid Movement : {valid_movement}\nCurrent Status: {current_status}\n"

    if crate_available == "yes":
        current_input += f"Crate reason: {crate_reason}\nCrate action: {crate_action}\n"

    if in_danger == "yes":
        if escape_bomb_action not in valid_movement:
            valid_movement.append(escape_bomb_action)
        current_input += f"Are you in a bomb radius : {in_bomb_radius}\nIn Danger of bomb : {in_danger}\nEscape from Bomb : {escape_bomb_action}\n"

    if plant_bomb == "true":
        if "BOMB" not in valid_movement:
            valid_movement.append("BOMB")
        current_input += f"Plant Bomb Reason: {plant_bomb_reason}\n"

    if coin_available == "yes":
        if coin_action not in valid_movement:
            valid_movement.append(coin_action)
        current_input += f"Collect Coins Action : {coin_action}\nReason for coins : {coin_reason}\n"

    # Add opponent predictions to input
    if opponent_predictions:
        current_input += "\n--- Opponent Predictions ---\n"
        for opp_name, prediction in opponent_predictions.items():
            opp_action = prediction.get("action", "UNKNOWN")
            opp_reasoning = prediction.get("reasoning", "No reasoning available")
            current_input += f"Opponent {opp_name}:\n  Predicted Action: {opp_action}\n  Reasoning: {opp_reasoning}\n\n"

    movement_input = ""
    if movement_history:
        movement_input = "Last 5 Moves :\n"
        for m in movement_history:
            movement_input += f"Action : {m.get('action')}, Reason : {m.get('reasoning')}\n"
        final_input = movement_input + "\n" + current_input
    else:
        final_input = current_input

    # Step 3: Create main orchestrator agent with opponent predictions
    agent = BombermanAgent()
    await agent.initialise_agent(need_reasoning, game_state, valid_movement, in_bomb_radius, plant_bomb_available)
    results = await agent.run_agent(final_input)
    results['valid_movement'] = valid_movement
    results['opponent_predictions'] = opponent_predictions

    return results


async def predict_opponent_move(need_reasoning, opponent_data, game_state, valid_movement, check_bomb_radius, plant_bomb_available):
    """
    Use PredictAgent to predict a single opponent's next move.

    Args:
        need_reasoning: Whether to use reasoning model
        opponent_data: Dict containing opponent analysis
        game_state: Current game state
        valid_movement: Valid movements for our agent
        check_bomb_radius: Bomb danger data
        plant_bomb_available: Bomb planting data

    Returns:
        Dict with predicted action and reasoning
    """
    try:
        opp_name = opponent_data.get("name", "Unknown")
        opp_position = opponent_data.get("position", [0, 0])
        opp_distance = opponent_data.get("distance_to_us", 0)
        opp_in_danger = opponent_data.get("in_danger", False)
        opp_escape_routes = opponent_data.get("escape_routes", [])
        opp_bombs_available = opponent_data.get("bombs_available", 0)
        opp_score = opponent_data.get("score", 0)
        opp_score_diff = opponent_data.get("score_diff", 0)
        opp_valid_moves = opponent_data.get("valid_moves", [])
        opp_last_actions = opponent_data.get("last_3_actions", [])
        opp_nearest_coin_dir = opponent_data.get("nearest_coin_direction", None)
        opp_nearest_crate_dir = opponent_data.get("nearest_crate_direction", None)
        opp_can_bomb_us = opponent_data.get("can_bomb_us", False)

        # Build input for predict agent
        predict_input = f"""
Opponent: {opp_name}
Position: {opp_position}
Distance to us: {opp_distance}

Status:
- In danger: {opp_in_danger}
- Escape routes: {opp_escape_routes}
- Bombs available: {opp_bombs_available}
- Score: {opp_score} (Score difference: {opp_score_diff})
- Valid moves: {opp_valid_moves}

Recent behavior:
- Last 3 positions: {opp_last_actions}

Intent indicators:
- Nearest coin direction: {opp_nearest_coin_dir}
- Nearest crate direction: {opp_nearest_crate_dir}
- Can bomb us: {opp_can_bomb_us}

Based on this information, predict what action this opponent will take next.
Consider:
1. If they're in danger, they'll likely try to escape
2. If they can collect coins easily, they might go for it
3. If they're aggressive and can bomb us, they might attack
4. Their recent movement patterns indicate their strategy
"""

        # Create and run predict agent
        predict_agent = PredictAgent()
        await predict_agent.initialise_agent(need_reasoning, game_state, opp_valid_moves, check_bomb_radius, plant_bomb_available)
        prediction = await predict_agent.run_agent(predict_input)

        return prediction

    except Exception as e:
        print(f"Error predicting opponent {opponent_data.get('name', 'Unknown')}: {str(e)}")
        return {"action": "UNKNOWN", "reasoning": f"Prediction failed: {str(e)}"}
