from workers import WorkerEntrypoint, Response
from statistics import mean
import json

from src.anchor_sets import AnchorSets
from src.ssr_rater import SSR_Rater
from src.synthetic_consumer import SyntheticConsumer


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "OPTIONS":
            return Response(
                "",
                status=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        if request.method == "POST":
            return await self.handle_evaluate(request)
        else:
            return Response(
                json.dumps({"error": "Method not allowed. Use POST /evaluate"}),
                status=405,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )

    async def handle_evaluate(self, request):
        """Evaluate product for a demographic profile - stateless."""
        try:
            body = await request.json()
            image = body.get("image")
            demographic_profile = body.get("demographic_profile")
            question = body.get(
                "question", "How likely would you be to buy this product?"
            )

            if not image or not demographic_profile:
                return Response(
                    json.dumps({"error": "Missing image or demographic_profile"}),
                    status=400,
                    headers={
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                )

            account_id = self.env.CLOUDFLARE_ACCOUNT_ID
            api_key = self.env.CLOUDFLARE_API_KEY

            rater = SSR_Rater(account_id=account_id, api_key=api_key)
            synthetic_consumer = SyntheticConsumer(
                demographic_profile, account_id=account_id, api_key=api_key
            )

            response_text = synthetic_consumer.evaluate_product(image, question)

            anchor_sets = AnchorSets.SETS.values()
            distributions = [
                rater.get_likert_distribution(response_text, list(anchors))
                for anchors in anchor_sets
            ]

            mean_rating = mean(
                [
                    sum(pmf[i] * (i + 1) for i in range(len(pmf)))
                    for pmf in distributions
                ]
            )

            return Response(
                json.dumps(
                    {
                        "success": True,
                        "demographic_profile": demographic_profile,
                        "response": response_text,
                        "distributions": distributions,
                        "mean_rating": mean_rating,
                    }
                ),
                status=200,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
