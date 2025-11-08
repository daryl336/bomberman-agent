#!/bin/bash
# Quick test for agentic-predict endpoint using curl

echo "======================================"
echo "Testing Agentic Predict Endpoint"
echo "======================================"
echo ""

curl -X POST "http://0.0.0.0:6000/agentic-predict" \
  -H "Content-Type: application/json" \
  -d @test_payload.json \
  | jq '.'

echo ""
echo "======================================"
echo "Test Complete"
echo "======================================"
