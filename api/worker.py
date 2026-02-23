from workers import WorkerEntrypoint, Response
from statistics import mean
import json

from src.anchor_sets import AnchorSets
from src.ssr_rater import SSR_Rater
from src.synthetic_consumer import SyntheticConsumer

# CORS headers for all responses
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Handle CORS preflight
        if request.method == "OPTIONS":
            return Response("", status=200, headers=CORS_HEADERS)

        # Health check
        if request.method == "GET":
            return Response(
                json.dumps({
                    "status": "ok",
                    "service": "synthetic-market-research-python-api",
                    "has_credentials": bool(
                        self.env.CLOUDFLARE_ACCOUNT_ID and self.env.CLOUDFLARE_API_KEY
                    ),
                }),
                status=200,
                headers=CORS_HEADERS,
            )

        # Evaluation endpoint
        if request.method == "POST":
            return await self.handle_evaluate(request)

        # Method not allowed
        return Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            headers=CORS_HEADERS,
        )

    async def handle_evaluate(self, request):
        """Evaluate product for a demographic profile."""
        try:
            body = await request.json()
            image = body.get("image")
            demographic_profile = body.get("demographic_profile")
            question = body.get("question", "How likely would you be to buy this product?")

            if not image or not demographic_profile:
                return Response(
                    json.dumps({"error": "Missing image or demographic_profile"}),
                    status=400,
                    headers=CORS_HEADERS,
                )

            # Initialize AI components
            rater = SSR_Rater(
                account_id=self.env.CLOUDFLARE_ACCOUNT_ID,
                api_key=self.env.CLOUDFLARE_API_KEY
            )
            consumer = SyntheticConsumer(
                demographic_profile,
                account_id=self.env.CLOUDFLARE_ACCOUNT_ID,
                api_key=self.env.CLOUDFLARE_API_KEY
            )

            # Get AI evaluation
            response_text = consumer.evaluate_product(image, question)

            # Calculate sentiment distributions
            distributions = [
                rater.get_likert_distribution(response_text, list(anchors))
                for anchors in AnchorSets.SETS.values()
            ]

            # Calculate mean rating
            mean_rating = mean([
                sum(pmf[i] * (i + 1) for i in range(len(pmf)))
                for pmf in distributions
            ])

            return Response(
                json.dumps({
                    "success": True,
                    "demographic_profile": demographic_profile,
                    "response": response_text,
                    "distributions": distributions,
                    "mean_rating": mean_rating,
                }),
                status=200,
                headers=CORS_HEADERS,
            )

        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers=CORS_HEADERS,
            )
