# Copyright (c) Microsoft. All rights reserved.

import asyncio
import logging
import os

from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from agents.code_validation_agent import CodeValidationAgent
from agents.content_creation_agent import ContentCreationAgent
from agents.user_agent import UserAgent
from custom_selection_strategy import CustomSelectionStrategy
from custom_termination_strategy import CustomTerminationStrategy
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents import AuthorRole, ChatMessageContent

"""
Note: This sample use the `AgentGroupChat` feature of Semantic Kernel, which is
no longer maintained. For a replacement, consider using the `GroupChatOrchestration`.
Read more about the `GroupChatOrchestration` here:
https://learn.microsoft.com/semantic-kernel/frameworks/agent/agent-orchestration/group-chat?pivots=programming-language-python
Here is a migration guide from `AgentGroupChat` to `GroupChatOrchestration`:
https://learn.microsoft.com/semantic-kernel/support/migration/group-chat-orchestration-migration-guide?pivots=programming-language-python
"""

TASK = """
Create a blog post about how to create a custom plugin for Semantic Kernel.
The content of the blog post should include the following:
1. What are plugins in Semantic Kernel?
2. How do people use plugins in Semantic Kernel?
3. How do devs create custom plugins in Semantic Kernel?
    - Include a walk through of creating a custom plugin. 
    - Include a sample on how to use the plugin.
    - If a reader follows the walk through and the sample, they should be able to create their own plugin.

You can use the following files as examples:
plugins/repo_file_plugin.py
plugins/code_execution_plugin.py
plugins/user_plugin.py
"""


load_dotenv()
AZURE_APP_INSIGHTS_CONNECTION_STRING = os.getenv("AZURE_APP_INSIGHTS_CONNECTION_STRING")

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "Document Generator"})


def set_up_tracing():
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import set_tracer_provider

    # Initialize a trace provider for the application. This is a factory for creating tracers.
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=AZURE_APP_INSIGHTS_CONNECTION_STRING))
    )
    # Sets the global default tracer provider
    set_tracer_provider(tracer_provider)




async def main():
    if AZURE_APP_INSIGHTS_CONNECTION_STRING:
        set_up_tracing()

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("main"):
        agents = [
            ContentCreationAgent(),
            UserAgent(),
            CodeValidationAgent(),
        ]

        group_chat = AgentGroupChat(
            agents=agents,
            termination_strategy=CustomTerminationStrategy(agents=agents),
            selection_strategy=CustomSelectionStrategy(),
        )
        await group_chat.add_chat_message(
            ChatMessageContent(
                role=AuthorRole.USER,
                content=TASK.strip(),
            )
        )

        async for response in group_chat.invoke():
            print(f"==== {response.name} just responded ====")
            # print(response.content)

        content_history: list[ChatMessageContent] = []
        async for message in group_chat.get_chat_messages(agent=agents[0]):
            if message.name == agents[0].name:
                # The chat history contains responses from other agents.
                content_history.append(message)
        # The chat history is in descending order.
        print("Final content:")
        print(content_history[0].content)


if __name__ == "__main__":
    asyncio.run(main())