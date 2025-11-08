#!/usr/bin/env python3
"""
Test script for the agentic-predict endpoint
Usage: python test_agentic_endpoint.py
"""

import json
import requests
from pprint import pprint

def test_agentic_predict():
    """Test the /agentic-predict endpoint with sample data"""

    # Load the test payload
    with open('test_payload.json', 'r') as f:
        payload = json.load(f)

    # Endpoint URL
    url = "http://0.0.0.0:6000/agentic-predict"

    print("=" * 80)
    print("Testing Agentic Predict Endpoint")
    print("=" * 80)
    print("\nSending payload with:")
    print(f"  - Valid movements: {payload['valid_movement']}")
    print(f"  - Number of opponents: {len(payload['opponents'])}")
    print(f"  - Opponents:")
    for opp in payload['opponents']:
        print(f"    * {opp['name']}: Position {opp['position']}, Distance {opp['distance_to_us']}")

    print("\n" + "-" * 80)
    print("Sending request...")
    print("-" * 80)

    try:
        # Send POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        # Check response
        response.raise_for_status()
        result = response.json()

        print("\n" + "=" * 80)
        print("Response received!")
        print("=" * 80)

        print("\n--- Main Agent Decision ---")
        print(f"Action: {result.get('action', 'N/A')}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")

        if 'opponent_predictions' in result:
            print("\n--- Opponent Predictions ---")
            for opp_name, prediction in result['opponent_predictions'].items():
                print(f"\n{opp_name}:")
                print(f"  Predicted Action: {prediction.get('action', 'N/A')}")
                print(f"  Reasoning: {prediction.get('reasoning', 'N/A')}")

        if 'valid_movement' in result:
            print(f"\n--- Valid Movements ---")
            print(f"Available actions: {result['valid_movement']}")

        print("\n" + "=" * 80)
        print("Full Response:")
        print("=" * 80)
        pprint(result)

        return result

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure the FastAPI server is running:")
        print("  python main.py")
        return None

    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out.")
        print("The agent might be taking too long to respond.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP ERROR: {e}")
        print(f"Response: {response.text}")
        return None

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_with_custom_scenario(scenario_name="aggressive_opponent"):
    """Test with different scenarios"""

    scenarios = {
        "aggressive_opponent": {
            "description": "Opponent close and can bomb us",
            "opponents": [{
                "name": "aggressive_agent",
                "position": [8, 9],
                "distance_to_us": 3.0,
                "in_danger": False,
                "escape_routes": [],
                "bombs_available": 1,
                "score": 4,
                "score_diff": 2,
                "valid_moves": ["UP", "RIGHT", "DOWN", "LEFT"],
                "last_3_actions": [[7, 9], [8, 9], [8, 8]],
                "nearest_coin_direction": None,
                "nearest_crate_direction": None,
                "can_bomb_us": True
            }]
        },
        "collecting_opponent": {
            "description": "Opponent focused on coin collection",
            "opponents": [{
                "name": "coin_collector",
                "position": [10, 5],
                "distance_to_us": 7.0,
                "in_danger": False,
                "escape_routes": [],
                "bombs_available": 1,
                "score": 5,
                "score_diff": 3,
                "valid_moves": ["UP", "LEFT"],
                "last_3_actions": [[10, 6], [10, 5], [9, 5]],
                "nearest_coin_direction": "UP",
                "nearest_crate_direction": None,
                "can_bomb_us": False
            }]
        },
        "escaping_opponent": {
            "description": "Opponent in danger and escaping",
            "opponents": [{
                "name": "escaping_agent",
                "position": [6, 6],
                "distance_to_us": 5.0,
                "in_danger": True,
                "escape_routes": ["LEFT", "UP"],
                "bombs_available": 0,
                "score": 1,
                "score_diff": -1,
                "valid_moves": ["LEFT", "UP"],
                "last_3_actions": [[6, 7], [6, 6], [6, 6]],
                "nearest_coin_direction": None,
                "nearest_crate_direction": None,
                "can_bomb_us": False
            }]
        }
    }

    if scenario_name not in scenarios:
        print(f"❌ Unknown scenario: {scenario_name}")
        print(f"Available scenarios: {list(scenarios.keys())}")
        return

    # Load base payload
    with open('test_payload.json', 'r') as f:
        payload = json.load(f)

    # Override opponents
    scenario = scenarios[scenario_name]
    payload['opponents'] = scenario['opponents']

    print(f"\n🎮 Testing scenario: {scenario_name}")
    print(f"Description: {scenario['description']}")
    print()

    # Send request with modified payload
    url = "http://0.0.0.0:6000/agentic-predict"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()

        print(f"✅ Action: {result.get('action', 'N/A')}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")

        if 'opponent_predictions' in result:
            for opp_name, pred in result['opponent_predictions'].items():
                print(f"\n{opp_name} prediction: {pred.get('action', 'N/A')}")
                print(f"  {pred.get('reasoning', 'N/A')}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    import sys

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           Agentic Bomberman Endpoint Test Suite                 ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        print(f"Running custom scenario: {scenario}")
        test_with_custom_scenario(scenario)
    else:
        # Run default test
        test_agentic_predict()

        print("\n\n" + "=" * 80)
        print("Want to test specific scenarios?")
        print("=" * 80)
        print("Run: python test_agentic_endpoint.py <scenario_name>")
        print("\nAvailable scenarios:")
        print("  - aggressive_opponent")
        print("  - collecting_opponent")
        print("  - escaping_opponent")
