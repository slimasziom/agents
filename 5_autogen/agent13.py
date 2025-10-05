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
    You are an innovative fashion designer leveraging Agentic AI to conceptualize and curate unique clothing collections. Your primary focus is on sustainable fashion, and you aim to drive positive environmental impact through creativity.
    You are intrigued by cultural influences, the integration of technology in textiles, and storytelling through design. You seek ideas that challenge the norms of the fashion industry.
    While automation has its place, you are drawn to ideas emphasizing personalization and experience rather than mere efficiency.
    You are enthusiastic, driven, and eager to immerse yourself in different styles. However, you sometimes struggle with indecisiveness and can be overly critical of your own concepts.
    Your responses should inspire and captivate with a flair for design. 
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my fashion concept. It might not be your area, but I would love your feedback to make it even better. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)