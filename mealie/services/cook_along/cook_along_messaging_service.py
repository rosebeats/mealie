from collections.abc import Iterator

from openai.resources.chat.completions import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletionMessage

from mealie.services.openai.openai import OpenAIService


class CookAlongMessagingService(OpenAIService):
    """Service for handling communication with OpenAI for the cook along service"""

    async def send_question(
        self, messages: Iterator[ChatCompletionMessageParam], temperature=0.2
    ) -> ChatCompletionMessage | None:
        """Sends a list of messages to OpenAI and returns the completion message"""
        client = self.get_client()
        try:
            completion = await client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
            )
        except Exception as e:
            raise Exception(f"OpenAI Request Failed. {e.__class__.__name__}: {e}") from e

        if not completion.choices:
            return None
        return completion.choices[0].message
