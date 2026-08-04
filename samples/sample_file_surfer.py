import asyncio
import argparse
import yaml
import os
from pathlib import Path
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from magentic_ui.teams import RoundRobinGroupChat
from magentic_ui.agents import FileSurfer
from autogen_agentchat.agents import UserProxyAgent

# Configure logging to print to console


async def main(work_dir: str) -> None:    # Load configuration from config.yaml
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
      # Get the file_surfer_client from config
    model_config = config.get("file_surfer_client", config.get("model_config", {}))
    
    # For Azure model config with model_info, create custom OpenAI client
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # If using Azure provider, we'll use base OpenAI client with Azure API
    cfg = model_config.get("config", {}).copy()
    
    # Use model config directly as we've already configured it properly
    model_client = OpenAIChatCompletionClient(**cfg)

    termination = TextMentionTermination("EXITT")

    user_proxy = UserProxyAgent(name="user_proxy")

    file_surfer = FileSurfer(
        name="file_surfer",
        model_client=model_client,
        work_dir=work_dir,
        bind_dir=work_dir,
    )

    team = RoundRobinGroupChat(
        participants=[file_surfer, user_proxy],
        max_turns=30,
        termination_condition=termination,
    )
    await team.lazy_init()
    user_message = await asyncio.get_event_loop().run_in_executor(None, input, ">: ")

    stream = team.run_stream(task=user_message)
    await Console(stream)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run FileSurfer with a specified work directory."
    )
    parser.add_argument(
        "--work-dir",
        type=str,
        default="debug",
        help="Directory to use for file surfer.",
    )
    args = parser.parse_args()
    asyncio.run(main(args.work_dir))
