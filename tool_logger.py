from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, Usage, function_tool
import traceback

class ToolLogger(RunHooks):
    def __init__(self):
        self.event_counter = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _usage_to_str(self, usage) -> str:
        return (
            f"🧾 Usage → "
            f"{usage.requests} requests | "
            f"{usage.input_tokens} input tokens | "
            f"{usage.output_tokens} output tokens | "
            f"{usage.total_tokens} total tokens"
        )

    async def on_agent_start(self, context, agent) -> None:
        self.event_counter += 1
        self.total_input_tokens += context.usage.input_tokens
        self.total_output_tokens += context.usage.output_tokens
        print("\n" + "="*60)
        print(f"🚀 Event #{self.event_counter} → Agent: **{agent.name}** started")
        print(f"   {self._usage_to_str(context.usage)}")
        print("="*60)
    
    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: any) -> None:
        self.event_counter += 1
        self.total_input_tokens += context.usage.input_tokens
        self.total_output_tokens += context.usage.output_tokens
        print("\n" + "-"*60)
        print(f"🏁 Event #{self.event_counter} → Agent: **{agent.name}** ended")
        # print(f"   ↪ Output: {output}")
        print(f"   {self._usage_to_str(context.usage)}")
        print("-"*60)
        
    async def on_tool_start(self, context, agent, tool):
        print(f"[🛠 START] Agent: {agent.name} | Tool: {tool.name}")

    async def on_tool_end(self, context, agent, tool, result):
        print(f"[✅ END] Tool: {tool.name} by Agent: {agent.name}")
        # print(f"Output: {result}")
    
    async def on_tool_error(self, context, agent, tool, error):
        print(f"[❌ ERROR] Tool: {tool.name} failed with error: {error}")
        print(traceback.format_exc())