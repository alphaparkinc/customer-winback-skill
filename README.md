# customer-winback-skill

> **GenPark AI Agent Skill** -- Identify lapsed customers, score win-back potential, generate personalized offers, and build re-engagement email sequences.

## Features

- Win-back scoring (0-100) based on recency, spend, frequency, and AOV
- Value tiers: High / Medium / Low
- Lapse tiers: Recently Lapsed / Moderately Lapsed / Long Lapsed / At-Risk Churned
- Discount offer calibration by value tier + lapse tier
- Personalized email sequences (2-4 emails per tier)
- Revenue recovery potential estimate

## Quick Start

```python
from client import CustomerWinbackClient

client = CustomerWinbackClient()
result = client.run(
    customers=[{"id":"C1","days_since_purchase":95,"total_orders":5,"total_spend":350,"avg_order_value":70}],
    brand_name="MyStore",
    max_discount_pct=20,
)
for cust in result["prioritized_customers"]:
    print(f"{cust['name']}: Score {cust['winback_score']} | Offer: {cust['offer_discount_pct']}% off")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
