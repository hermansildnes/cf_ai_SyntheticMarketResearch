from typing import Dict, Union
import os
import requests
import base64


class SyntheticConsumer:
    def __init__(
        self,
        demographics: Dict[str, Union[str, int]],
        model: str = "@cf/meta/llama-3.1-8b-instruct",
    ):
        self.demographics = demographics
        self.model = model
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.auth_token = os.getenv("CLOUDFLARE_API_KEY")
        if not self.auth_token:
            raise ValueError("CLOUDFLARE_API_KEY environment variable is not set.")

    def _build_system_prompt(self) -> str:
        demo_description = "; ".join(
            f"{key}: {', '.join(value) if isinstance(value, list) else value}"
            for key, value in self.demographics.items()
        )

        return f"You are a consumer with the following demographic profile: {demo_description}. Respond authentically as someone with these characteristics would."

    def evaluate_product(
        self,
        base64_image: str,
        question: str = "How likely would you be to buy this product?",
        temperature: float = 1.0,
        max_tokens: int = 500,
        mime_type: str = "image/jpeg",
    ) -> str:
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "messages": [
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
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["result"]["choices"][0]["message"]["content"]
