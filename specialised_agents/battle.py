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

class BattleAgent():
    async def initialise_agent(self, need_reasoning, game_state, valid_movement, in_bomb_radius, plant_bomb_available, maverick=False):
        """
        Initialises the Battle-focused Bomberman agent with the necessary settings and tools.
        """
        self.name = "Battle Agent"
        self.need_reasoning = need_reasoning
        self.game_state = game_state
        self.valid_movement = valid_movement
        self.in_bomb_radius = in_bomb_radius
        self.plant_bomb_available = plant_bomb_available
        self.maverick = maverick
        
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
        Role: You are an aggressive battle-focused Bomberman agent. Your main goal is to dominate the battlefield by destroying crates and eliminating opponents while maintaining your own survival.

        Tasks:
        1. Destroy crates strategically to control the map and create advantageous positions.
        2. Eliminate opponents by trapping them with bombs or forcing them into dangerous positions.
        3. Collect coins opportunistically when safe to do so.
        4. Survive by escaping danger and maintaining safe positioning.

        Inputs:
        - List of valid movements available for you to choose.
        - Information on whether you are in any bomb blast radius.
        - Reason for planting a bomb, if available.
        - Movement history to track past actions.
        - Opponent predictions including their positions, intentions, and vulnerabilities.

        Expected Outputs:
        - Provide a reason for your chosen actions.
        - Specify the action to be taken.

        Additional Information:
        - Prioritize survival first: If you are in danger, ALWAYS escape immediately.
        - Prioritize offensive opportunities second: Look for chances to trap opponents or destroy multiple crates.
        - Prioritize coin collection third: Only collect coins when it doesn't compromise safety or offensive positioning.
        - When planting bombs, ensure you have a clear escape route before committing.
        - Consider opponent predictions to anticipate their moves and set traps.
        - Use bombs to control territory and limit opponent movement options.
        - If you decide to plant a bomb, return "BOMB" for your action.
        - Be aggressive but calculated - a dead agent scores nothing.
        - Look for opportunities to corner opponents by predicting their escape routes.
        - Destroy crates to reveal coins and reduce opponent hiding spots.
        """
        if self.maverick:
            specialist_instructions += """- You will also have additional input from your friend Maverick. Take into consideration of Maverick actions. Overwrite it if it is dangerous and not feasible. Remember your priorities and stay on course."""
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
    
    