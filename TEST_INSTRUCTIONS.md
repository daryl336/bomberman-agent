# Testing the Agentic Predict Endpoint

## Overview

The `/agentic-predict` endpoint uses an agentic architecture where:
1. **Main Orchestrator Agent** receives tactical game data + opponent analysis
2. **PredictAgent** (one per opponent) predicts each opponent's next move in parallel
3. **Main Agent** uses predictions to make final strategic decision

---

## Prerequisites

1. **Start the FastAPI server:**
   ```bash
   cd "/Users/daryltay/Documents/NUS Masters/CS5446 AI Planning/bomberman-agent"
   python main.py
   ```

2. **Ensure environment variables are set:**
   - `OPENAI_DEPLOYMENT_NAME` (for normal mode)
   - `GPT5` (for reasoning mode)
   - OpenAI API credentials

---

## Testing Methods

### Method 1: Python Test Script (Recommended)

**Basic test with sample payload:**
```bash
python test_agentic_endpoint.py
```

**Test specific scenarios:**
```bash
# Test aggressive opponent scenario
python test_agentic_endpoint.py aggressive_opponent

# Test collecting opponent scenario
python test_agentic_endpoint.py collecting_opponent

# Test escaping opponent scenario
python test_agentic_endpoint.py escaping_opponent
```

### Method 2: Curl Command

```bash
# Make sure test_curl.sh is executable
chmod +x test_curl.sh

# Run the test
./test_curl.sh
```

Or manually:
```bash
curl -X POST "http://0.0.0.0:6000/agentic-predict" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Method 3: Using Python requests directly

```python
import requests
import json

with open('test_payload.json', 'r') as f:
    payload = json.load(f)

response = requests.post(
    "http://0.0.0.0:6000/agentic-predict",
    json=payload,
    headers={'Content-Type': 'application/json'}
)

print(response.json())
```

---

## Sample Payload Structure

The `test_payload.json` contains a realistic game scenario with:

### Game Context
- **Valid movements:** `["UP", "RIGHT", "DOWN", "LEFT"]`
- **Nearest crate:** 3.0 distance, direction RIGHT
- **Bomb status:** Not in danger, no bomb detected
- **Coin status:** Available, direction UP

### Opponent Data (3 opponents)

#### 1. rule_based_agent
```json
{
  "name": "rule_based_agent",
  "position": [5, 7],
  "distance_to_us": 8.0,
  "in_danger": false,
  "bombs_available": 1,
  "score": 3,
  "score_diff": 1,
  "nearest_coin_direction": "UP",
  "can_bomb_us": false
}
```

#### 2. ppo_agent (in danger)
```json
{
  "name": "ppo_agent",
  "position": [12, 3],
  "distance_to_us": 6.0,
  "in_danger": true,
  "escape_routes": ["LEFT"],
  "bombs_available": 0,
  "score": 2
}
```

#### 3. aggressive_agent (threat)
```json
{
  "name": "aggressive_agent",
  "position": [8, 9],
  "distance_to_us": 4.0,
  "bombs_available": 1,
  "can_bomb_us": true
}
```

---

## Expected Response

The response will include:

```json
{
  "reasoning": "Detailed reasoning considering tactical situation and opponent predictions",
  "action": "UP|RIGHT|DOWN|LEFT|WAIT|BOMB",
  "valid_movement": ["UP", "RIGHT", "DOWN", "LEFT"],
  "opponent_predictions": {
    "rule_based_agent": {
      "action": "UP",
      "reasoning": "Agent is moving toward nearest coin..."
    },
    "ppo_agent": {
      "action": "LEFT",
      "reasoning": "Agent is in danger and escaping..."
    },
    "aggressive_agent": {
      "action": "BOMB",
      "reasoning": "Agent can bomb us and is aggressive..."
    }
  }
}
```

---

## Customizing Test Payload

Edit `test_payload.json` to test different scenarios:

### Example: Test escaping from danger

```json
{
  "check_bomb_radius": {
    "in_bomb_radius": "yes",
    "in_danger": "yes",
    "escape_bomb_action": "LEFT"
  },
  "opponents": [
    {
      "name": "bomber",
      "position": [9, 10],
      "distance_to_us": 2.0,
      "bombs_available": 1,
      "can_bomb_us": true,
      "last_3_actions": [[8, 10], [9, 10], [9, 10]],
      "nearest_coin_direction": null
    }
  ]
}
```

### Example: Test coin race scenario

```json
{
  "coins_collection_policy": {
    "coin_available": "yes",
    "coin_action": "UP",
    "coin_reason": "Coins are reachable."
  },
  "opponents": [
    {
      "name": "coin_racer",
      "position": [10, 8],
      "distance_to_us": 3.0,
      "nearest_coin_direction": "UP",
      "last_3_actions": [[10, 9], [10, 8], [10, 7]],
      "score_diff": 2
    }
  ]
}
```

---

## Troubleshooting

### Server not responding
```bash
# Check if server is running
curl http://0.0.0.0:6000/

# Check server logs for errors
```

### Timeout errors
- Increase timeout in test script (default: 60 seconds)
- Check if LLM API is responding
- Verify OpenAI API keys are valid

### Import errors
```bash
# Install required packages
pip install requests pprint
```

### JSON parsing errors
- Validate test_payload.json using: `jq . test_payload.json`
- Ensure all fields match expected types

---

## Monitoring Performance

The agentic architecture runs opponent predictions in **parallel**, so with 3 opponents:

- **Sequential time:** ~15-20 seconds (5-7s per opponent prediction)
- **Parallel time:** ~5-7 seconds (all predictions at once)
- **Speedup:** ~3x faster

Monitor in server logs:
```
Processing a request for agentic prediction.
[PredictAgent] Analyzing rule_based_agent...
[PredictAgent] Analyzing ppo_agent...
[PredictAgent] Analyzing aggressive_agent...
[Orchestrator] All predictions received, making final decision...
```

---

## Integration with Bomberman Game

To use in actual game, update `callbacks.py` endpoint:
```python
BOMBERMAN_AGENT_ENDPOINT = "http://0.0.0.0:6000/agentic-predict"
```

The game will automatically:
1. Analyze all opponents using `analyze_all_opponents()`
2. Send payload with opponent data
3. Receive action with opponent predictions
4. Execute action in game

---

## Next Steps

1. **Test basic payload:** `python test_agentic_endpoint.py`
2. **Verify opponent predictions:** Check logs for PredictAgent outputs
3. **Test scenarios:** Run different opponent configurations
4. **Integrate with game:** Run actual Bomberman game with llm_predict agent
5. **Monitor performance:** Analyze prediction accuracy and decision quality
