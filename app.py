import os
from statistics import mean
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from src.anchor_sets import AnchorSets
from src.ssr_rater import SSR_Rater
from src.synthetic_consumer import SyntheticConsumer


app = FastAPI(
    title="Synthetic Market Research API",
    description="AI-powered market research using synthetic consumers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Synthetic Market Research API",
        "version": "1.0.0"
    }


@app.post("/evaluate")
def evaluate_product(
    image: str,
    demographic_profile: Dict[str, Any],
    question: str = "How likely would you be to buy this product?",
):
    """
    Evaluate a product using a single synthetic consumer.
    """
    rater = SSR_Rater()
    anchor_sets = AnchorSets.SETS.values()

    synthetic_consumer = SyntheticConsumer(demographic_profile)

    response = synthetic_consumer.evaluate_product(image, question)
    consumer_distributions = []
    for anchors in anchor_sets:
        distribution = rater.get_likert_distribution(response, anchors)
        consumer_distributions.append(distribution)

    mean_rating = mean(
        [sum(pmf[i] * (i + 1) for i in range(len(pmf))) for pmf in consumer_distributions]
    )

    return {
        "response": response,
        "distributions": consumer_distributions,
        "mean_rating": mean_rating
    }
