import numpy as np
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import matplotlib.pyplot as plt
import asyncio
from anchor_sets import AnchorSets
from ssr_rater import SSR_Rater
from synthetic_customer import SyntheticCustomer
from demographics import DemographicProfiles


async def main():
    load_dotenv()

    async_client = AsyncOpenAI(api_key=os.getenv("API_KEY"))

    rater = SSR_Rater(async_client)

    anchor_sets = AnchorSets.get_all()
    demographic_profiles = DemographicProfiles.get_first_n(40)

    synthetic_customers = [
        SyntheticCustomer(async_client, profile, model="gpt-4o-mini")
        for profile in demographic_profiles
    ]

    image_path = "data/ad3.png"
    question = "How likely would you be to buy this product?"

    print(
        f"Evaluating product with {len(synthetic_customers)} synthetic customers...\n"
    )
    print(f"Running {len(synthetic_customers) * 2} evaluations concurrently...")

    all_tasks = []
    for customer in synthetic_customers:
        all_tasks.append(customer.evaluate_product(image_path, question))
        all_tasks.append(customer.evaluate_product(image_path, question))

    print("Waiting for LLM responses...")
    all_responses = await asyncio.gather(*all_tasks)
    print(f"Received {len(all_responses)} responses\n")

    print("Computing Likert distributions...")

    all_likert_tasks = []
    for response in all_responses:
        for anchors in anchor_sets:
            all_likert_tasks.append(rater.get_likert_distribution(response, anchors))

    print(f"Computing {len(all_likert_tasks)} likert distributions concurrently...")
    all_pmfs = await asyncio.gather(*all_likert_tasks)

    customer_mean_ratings = []
    pmfs_per_response = len(anchor_sets)

    for i in range(0, len(all_responses), 2):
        idx1 = i * pmfs_per_response
        idx2 = (i + 1) * pmfs_per_response

        response1_pmfs = all_pmfs[idx1 : idx1 + pmfs_per_response]
        response2_pmfs = all_pmfs[idx2 : idx2 + pmfs_per_response]

        avg_pmfs = [
            (pmf1 + pmf2) / 2 for pmf1, pmf2 in zip(response1_pmfs, response2_pmfs)
        ]

        ratings = [np.dot(pmf, np.arange(1, 6)) for pmf in avg_pmfs]
        mean_rating = np.mean(ratings)
        customer_mean_ratings.append(mean_rating)

        customer_num = i // 2 + 1
        print(f"  Customer {customer_num}: {mean_rating:.2f}")

    print(f"\nProcessed all ratings\n")

    print("Generating plots...")
    plot_likert_ratings(customer_mean_ratings)

    print("SUMMARY")
    print("=" * 70)
    print(f"Overall mean rating: {np.mean(customer_mean_ratings):.2f}")
    print(f"Std deviation: {np.std(customer_mean_ratings):.2f}")
    print(f"Min rating: {np.min(customer_mean_ratings):.2f}")
    print(f"Max rating: {np.max(customer_mean_ratings):.2f}")


def plot_likert_ratings(mean_ratings):
    """Plot the distribution of mean likert ratings."""
    from scipy import stats

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    mean_ratings = np.array(mean_ratings)

    # Left plot: Histogram with normal distribution overlay
    n_bins = min(15, len(mean_ratings) // 2 + 1)
    counts, bins, patches = ax1.hist(
        mean_ratings,
        bins=n_bins,
        alpha=0.7,
        edgecolor="black",
        density=True,
        label="Observed",
    )

    # Fit and plot normal distribution
    mu, std = np.mean(mean_ratings), np.std(mean_ratings)
    x = np.linspace(mean_ratings.min(), mean_ratings.max(), 100)
    ax1.plot(
        x,
        stats.norm.pdf(x, mu, std),
        "r-",
        linewidth=2,
        label=f"Normal(μ={mu:.2f}, σ={std:.2f})",
    )

    # Add mean line
    ax1.axvline(mu, color="blue", linestyle="--", linewidth=2, alpha=0.7, label="Mean")

    ax1.set_xlabel("Mean Likert Rating (1-5)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Density", fontsize=12, fontweight="bold")
    ax1.set_title("Distribution of Customer Ratings", fontsize=14, fontweight="bold")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # Right plot: Q-Q plot to check normality
    stats.probplot(mean_ratings, dist="norm", plot=ax2)
    ax2.set_title("Q-Q Plot (Normality Check)", fontsize=14, fontweight="bold")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("likert_ratings.png", dpi=300, bbox_inches="tight")
    print("Plot saved as 'likert_ratings.png'")
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())
