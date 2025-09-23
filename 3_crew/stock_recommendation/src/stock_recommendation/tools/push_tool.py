from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class PushNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str:
        pushover_user = os.getenv("PUSHOVER_USER")
        pushover_token = os.getenv("PUSHOVER_TOKEN")
        pushover_url = "https://api.pushover.net/1/messages.json"

        if not pushover_user or not pushover_token:
            raise ValueError("PUSHOVER_USER and PUSHOVER_TOKEN must be set")
        
        print(f"Push: {message}")
        payload = {"user": pushover_user, "token": pushover_token, "message": message}
        response = requests.post(pushover_url, data=payload)
        response.raise_for_status()
        return '{"notification": "ok"}'
