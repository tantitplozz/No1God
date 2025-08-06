import asyncio
import base64
import os
from playwright.async_api import Page
from openai import OpenAI

class ToolsetVision:
    """
    ToolsetVision provides methods for interacting with web elements using Vision models (VLM).
    """

    def __init__(self, page: Page):
        self.page = page
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )

    async def _capture_and_encode_screenshot(self) -> str:
        """
        Captures a screenshot of the current page and encodes it to base64.
        """
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode("utf-8")

    async def solve_captcha(self, prompt: str = "What is the text in the CAPTCHA image?") -> str | None:
        """
        Uses a Vision model to solve a CAPTCHA.
        """
        try:
            base64_image = await self._capture_and_encode_screenshot()
            response = self.client.chat.completions.create(
                model="gpt-4o", # Or another suitable VLM model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error solving CAPTCHA with Vision model: {e}")
            return None

    async def click_element_by_vision(self, target_description: str) -> bool:
        """
        Uses a Vision model to identify and click an element based on its description.
        The VLM should return coordinates or a clear instruction.
        """
        try:
            base64_image = await self._capture_and_encode_screenshot()
            response = self.client.chat.completions.create(
                model="gpt-4o", # Or another suitable VLM model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Identify the coordinates (x,y) of the element described as: 
                            \"{target_description}\". Respond only with the coordinates in the format x,y. 
                            If not found, respond with -1,-1."}, 
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=50,
            )
            coords_str = response.choices[0].message.content.strip()
            x, y = map(int, coords_str.split(","))

            if x == -1 or y == -1:
                print(f"Element '{target_description}' not found by vision model.")
                return False

            await self.page.mouse.click(x, y)
            await asyncio.sleep(random.uniform(0.5, 1.5)) # Human-like delay
            return True
        except Exception as e:
            print(f"Error clicking element by vision: {e}")
            return False

    async def get_text_by_vision(self, prompt: str) -> str | None:
        """
        Uses a Vision model to extract text from a specific area or context on the page.
        """
        try:
            base64_image = await self._capture_and_encode_screenshot()
            response = self.client.chat.completions.create(
                model="gpt-4o", # Or another suitable VLM model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error getting text by vision: {e}")
            return None




