from typing import Dict, Union
import base64
from pathlib import Path


class SyntheticCustomer:
    def __init__(
        self,
        client,
        demographics: Dict[str, Union[str, int]],
        model: str = "gpt-4o",
    ):
        self.client = client
        self.demographics = demographics
        self.model = model

    def _build_system_prompt(self) -> str:
        demo_parts = []

        for key, value in self.demographics.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            demo_parts.append(f"{key}: {value}")

        demo_description = "; ".join(demo_parts)

        system_prompt = f"""You are a consumer with the following demographic profile: {demo_description}.
        When evaluating products, you should respond authentically as someone with these characteristics would.
        *Your response may be positive, negative, neutral, or indifferent—reflect honestly, even if you have no interest in the product.*
        Consider how your demographics might influence your purchasing decisions, preferences, and perspectives.

        Here are some examples of possible attitudes:
        - Strongly interested in the product.
        - Probably interested, but with some reservations.
        - Neutral or undecided; maybe not for you.
        - Probably would not buy it, due to lack of interest, concerns, or personal fit.
        - Definitely would not buy it for any reason.

        Provide an honest, thoughtful response that reflects these possibilities. It's perfectly acceptable if the product does not appeal to you at all."""

        return system_prompt

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_image_mime_type(self, image_path: str) -> str:
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(ext, "image/jpeg")

    async def evaluate_product(
        self,
        image_path: str,
        question: str = "How likely would you be to buy this product?",
        temperature: float = 1.0,
        max_tokens: int = 500,
    ) -> str:
        base64_image = self._encode_image(image_path)
        mime_type = self._get_image_mime_type(image_path)

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                    {"type": "text", "text": question},
                ],
            },
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content
