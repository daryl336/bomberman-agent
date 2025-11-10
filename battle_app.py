from specialised_agents.battle import BattleAgent

async def battle_bot(need_reasoning, game_state, valid_movement, nearest_crate, check_bomb_radius, plant_bomb_available, coins_collection_policy, movement_history, opponents=[], maverick_top_actions="", maverick_features="", maverick_best_action=""):
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

    # Add opponent information for battle-focused decision making
    if opponents and len(opponents) > 0:
        current_input += "\n--- Opponent Intelligence ---\n"
        for idx, opp in enumerate(opponents):
            opp_name = opp.get("name", f"Opponent_{idx}")
            opp_position = opp.get("position", "Unknown")
            opp_distance = opp.get("distance_to_us", "Unknown")
            opp_in_danger = opp.get("in_danger", False)
            opp_escape_routes = opp.get("escape_routes", [])
            opp_bombs_available = opp.get("bombs_available", 0)
            opp_score = opp.get("score", 0)
            opp_score_diff = opp.get("score_diff", 0)
            opp_can_bomb_us = opp.get("can_bomb_us", False)
            opp_nearest_coin_dir = opp.get("nearest_coin_direction", None)
            opp_nearest_crate_dir = opp.get("nearest_crate_direction", None)

            current_input += f"\nOpponent: {opp_name}\n"
            current_input += f"  Position: {opp_position}, Distance: {opp_distance}\n"
            current_input += f"  Status: {'In danger' if opp_in_danger else 'Safe'}, Bombs available: {opp_bombs_available}\n"
            current_input += f"  Score: {opp_score} (Diff: {opp_score_diff})\n"

            if opp_can_bomb_us:
                current_input += f"  THREAT: This opponent can bomb you from their current position!\n"
            if opp_in_danger and opp_escape_routes:
                current_input += f"  Vulnerable: Trying to escape via {opp_escape_routes}\n"
            if opp_nearest_coin_dir:
                current_input += f"  Intent: Moving towards coin ({opp_nearest_coin_dir})\n"
            if opp_nearest_crate_dir:
                current_input += f"  Intent: Moving towards crate ({opp_nearest_crate_dir})\n"

        current_input += "\nBattle Strategy:\n"
        current_input += "- Look for opportunities to trap vulnerable opponents\n"
        current_input += "- Prioritize eliminating threats who can bomb you\n"
        current_input += "- Control territory by destroying crates strategically\n"
        current_input += "- Cut off opponent escape routes when they are in danger\n"

    movement_input = ""
    if movement_history:
        movement_input = "Last 5 Moves :\n"
        for m in movement_history:
            movement_input += f"Action : {m.get('action')}, Reason : {m.get('reasoning')}"
        final_input = movement_input +"\n"+current_input
    else:
        final_input = current_input
    if maverick_best_action:
        final_input += f"""Maverick Actions:{maverick_top_actions}\nMaverick Features:{maverick_features}\nMaverick Best Action: {maverick_best_action}"""
        maverick = True
    else:
        maverick = False
    agent = BattleAgent()
    await agent.initialise_agent(need_reasoning, game_state, valid_movement, in_bomb_radius, plant_bomb_available, maverick=maverick)
    results = await agent.run_agent(final_input)
    results['valid_movement'] = valid_movement
    return results
