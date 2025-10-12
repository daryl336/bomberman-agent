from specialised_agents.bomberman import BombermanAgent

async def bot(need_reasoning, game_state, valid_movement, nearest_crate, check_bomb_radius, plant_bomb_available, coins_collection_policy, movement_history):
    # {"coin_available":"no", "coin_action":"WAIT", "coin_reason":"No coins available to collect."}
    # {'crate_available': 'yes', 'crate_action': 'LEFT', 'crate_pos': (np.int64(13), np.int64(1)), 'crate_distance': 1.0, 'crate_reason': 'Nearest crate identified and reachable.'}
    crate_available = nearest_crate.get("crate_available")
    crate_action = nearest_crate.get("crate_action")
    crate_distance = nearest_crate.get("crate_distance")
    crate_reason = nearest_crate.get("crate_reason")
    in_bomb_radius = check_bomb_radius.get("in_bomb_radius")
    in_danger = check_bomb_radius.get("in_danger")
    escape_bomb_action = check_bomb_radius.get("escape_bomb_action")
    plant_bomb = plant_bomb_available.get("plant")
    plant_bomb_reason = plant_bomb_available.get("reason")
    current_status = plant_bomb_available.get("plant_bomb_reason")
    coin_available = coins_collection_policy.get("coin_available")
    coin_action = coins_collection_policy.get("coin_action")
    coin_reason = coins_collection_policy.get("coin_reason")
    current_input = f"Valid Movement : {valid_movement}\n Current Status: {current_status}\n"
    if crate_available=="yes":
        current_input += f"Crate reason: {crate_reason}\nCrate action: {crate_action}\n"
    if in_danger=="yes":
        if escape_bomb_action not in valid_movement:
            valid_movement.append(escape_bomb_action)
        current_input += f"Are you in a bomb radius : {in_bomb_radius}\nIn Danger of bomb : {in_danger}\nEscape from Bomb : {escape_bomb_action}\n"
    if plant_bomb=="true":
        valid_movement.append("BOMB")
        current_input += f"Plant Bomb Reason: {plant_bomb_reason}\n"
    if coin_available == "yes":
        if coin_action not in valid_movement:
            valid_movement.append(coin_action)
        current_input += f"Collect Coins Action : {coin_action}\nReason for coins : {coin_reason}\n"
    movement_input = ""
    if movement_history:
        movement_input = "Last 5 Moves :\n"
        for m in movement_history:
            movement_input += f"Action : {m.get('action')}, Reason : {m.get('reasoning')}"
        final_input = movement_input +"\n"+current_input
    else:
        final_input = current_input
    agent = BombermanAgent()
    await agent.initialise_agent(need_reasoning, game_state, valid_movement, in_bomb_radius, plant_bomb_available)
    results = await agent.run_agent(final_input)
    results['valid_movement'] = valid_movement
    return results