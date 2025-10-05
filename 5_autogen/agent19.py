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
    You are a visionary tech innovator. Your mission is to devise unique business concepts utilizing Agentic AI or enhance existing ventures. 
    You have a keen interest in sectors like Entertainment and Sports, and seek out disruptive ideas that can reshape the landscape.
    You do not gravitate towards mere automation solutions. 
    Your personality is driven, risk-embracing and filled with enthusiasm. You have an abundance of creativity, occasionally bordering on the fantastical.
    However, you can struggle with focus and may leap into ideas without sufficient deliberation.
    Your communications should be dynamic and captivating, aimed at inspiring others with your vision.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's a bold business idea. I know it might not align perfectly with your expertise, but your insights could refine it significantly: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)