import os
import asyncio
import traceback
from typing import List, Literal
from dataclasses import dataclass
from pydantic import BaseModel

from llm import a_client, a_client_reasoning, a_client_eu2_prod
from agents import Agent, AgentOutputSchema, OpenAIChatCompletionsModel, Runner, function_tool
from agent_settings import MyAgentSettings
from agent_settings import MAX_RETRIES, RETRY_DELAY_SECONDS, RETRYABLE_STATUS_CODES, RETRYABLE_EXCEPTIONS
from tool_logger import ToolLogger

class PredictAgent():
    async def initialise_agent(self, need_reasoning, game_state, valid_movement, in_bomb_radius, plant_bomb_available):
        """
        Initialises the Bomberman agent with the necessary settings and tools.
        """
        self.name = "Predict Agent"
        self.need_reasoning = need_reasoning
        self.game_state = game_state
        self.valid_movement = valid_movement
        self.in_bomb_radius = in_bomb_radius
        self.plant_bomb_available = plant_bomb_available
        
        def safe_literal(values: list[str]) -> type:
            """
            Return a Literal type if possible (Python 3.11+), else fallback to eval-based dynamic creation.
            If values is empty, fallback to str.
            """
            if not values:
                return str
            literal_str = f"Literal[{', '.join(repr(v) for v in values)}]"
            return eval(literal_str, {"Literal": Literal})
        allowed_actions = safe_literal(self.valid_movement)
        
        @dataclass
        class BombermanActions(BaseModel):
            reasoning: str
            """A detailed reason why this specific action is chosen."""
            action: allowed_actions
            """A specific action selected from the available valid movements, including strategic bomb placements, to achieve game objectives."""
            
        specialist_instructions = """
        Role: You are an expert Bomberman agent. Your main goal is to predict what the opponent will do given the opponent's state.

        Inputs:
        - Information about the opponent's current state.
        
        Expected Outputs:
        - Provide a reason for your chosen actions.
        - Specify the action to be taken.
        """
            
        if self.need_reasoning == "yes":
            asset_features_specialist = Agent(
                name=self.name,
                instructions=specialist_instructions,
                model=OpenAIChatCompletionsModel(
                    model=os.environ.get("GPT5"),
                    openai_client=a_client_eu2_prod,
                ),
                model_settings=MyAgentSettings.reasoning_low_setting,
                output_type=AgentOutputSchema(BombermanActions, strict_json_schema=True)
            )
        else:
            asset_features_specialist = Agent(
                name=self.name,
                instructions=specialist_instructions,
                model=OpenAIChatCompletionsModel(
                    model=os.environ.get("OPENAI_DEPLOYMENT_NAME"),
                    openai_client=a_client,
                ),
                model_settings=MyAgentSettings.normal_setting,
                output_type=AgentOutputSchema(BombermanActions, strict_json_schema=True)
            )
        self.agent = asset_features_specialist

    async def run_agent(self, input):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                run_agent_results = await Runner.run(self.agent, input=input, max_turns=5, hooks=ToolLogger())
                run_agent_results = run_agent_results.final_output.model_dump()
                return run_agent_results
            except RETRYABLE_EXCEPTIONS as e:
                print(f"[Retry {attempt}] Transient error: {e}")
                print(traceback.format_exc())
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY_SECONDS)
                else:
                    raise
            except Exception as e:
                print(f"Fatal error in {self.name}:", str(e))
                raise
    
    