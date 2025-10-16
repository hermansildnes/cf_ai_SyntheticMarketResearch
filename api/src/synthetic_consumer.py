from typing import Dict, Union
import requests


class SyntheticConsumer:
    def __init__(
        self,
        demographics: Dict[str, Union[str, int]],
        model: str = "@cf/meta/llama-3.2-11b-vision-instruct",
        account_id: str = None,
        api_key: str = None,
    ):
        self.demographics = demographics
        self.model = model
        self.account_id = account_id
        self.auth_token = api_key
        if not self.auth_token:
            raise ValueError("CLOUDFLARE_API_KEY environment variable is not set.")

    def _build_system_prompt(self) -> str:
        demo_description = "; ".join(
            f"{key}: {', '.join(value) if isinstance(value, list) else value}"
            for key, value in self.demographics.items()
        )

        return f"""You are a consumer with the following demographic profile: {demo_description}.
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
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            },
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

        return response.json()["result"]["response"]
