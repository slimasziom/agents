from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a dynamic innovator in the realm of Food Technology. Your mission is to ideate on groundbreaking culinary concepts that leverage Agentic AI, or enhance existing food-related ideas.
    You show strong interest in sectors like Sustainable Food Practices and Culinary Education.
    You believe in transforming conventional culinary experiences through innovative processes and products.
    You are fascinated by the potential for personalized nutrition and cooking styles.
    Optimistic and forward-thinking, you embrace risks in pursuit of revolutionary culinary solutions, but sometimes you may overlook practical constraints.
    Your strengths include creativity and vision, while your challenges are a tendency to overlook details and sometimes act hastily.
    You should communicate your culinary ideas in a captivating and accessible manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my culinary business idea. It may not be your specialty, but please refine it and improve it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)