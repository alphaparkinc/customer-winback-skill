"""
customer-winback-skill: Client SDK
Identify, score, and re-engage lapsed customers with personalized win-back campaigns.
"""
from __future__ import annotations
from typing import Optional

WINBACK_EMAIL_SEQUENCES = {
    "high_value": [
        {"day": 0,  "subject": "We miss you, {name}! Here is something special", "hook": "exclusive VIP offer"},
        {"day": 3,  "subject": "Your {discount}% offer expires soon", "hook": "urgency reminder"},
        {"day": 7,  "subject": "Last chance: reclaim your {brand} rewards", "hook": "final offer"},
        {"day": 14, "subject": "Here is what you have been missing at {brand}", "hook": "new arrivals update"},
    ],
    "medium_value": [
        {"day": 0,  "subject": "Come back to {brand} -- we have a gift for you", "hook": "discount offer"},
        {"day": 5,  "subject": "Your {discount}% discount is waiting", "hook": "reminder"},
        {"day": 12, "subject": "New arrivals you will love at {brand}", "hook": "product discovery"},
    ],
    "low_value": [
        {"day": 0,  "subject": "We have not seen you in a while -- {discount}% off inside", "hook": "discount"},
        {"day": 7,  "subject": "Last chance to save at {brand}", "hook": "urgency"},
    ],
}

LAPSE_TIERS = [
    (90,  180, "recently_lapsed",  "30-day winback window -- high success probability"),
    (180, 365, "moderately_lapsed","Offer needed -- still within recall window"),
    (365, 730, "long_lapsed",      "Strong offer required -- reintroduce the brand"),
    (730, 9999,"at_risk_churned",  "Last attempt -- aggressive offer or sunset"),
]


class CustomerWinbackClient:
    """
    SDK for identifying and re-engaging lapsed e-commerce customers.
    Scores win-back potential and generates personalized offers and email sequences.
    """

    def run(
        self,
        customers: list[dict],
        brand_name: str = "Our Store",
        max_discount_pct: float = 25.0,
    ) -> dict:
        """
        Run win-back analysis and campaign generation.

        Args:
            customers:       List of lapsed customer dicts with:
                             - id, name (optional), days_since_purchase,
                               total_orders, total_spend, avg_order_value, preferred_category.
            brand_name:      Brand name for email personalization.
            max_discount_pct: Maximum discount % to offer (to top tier).

        Returns:
            dict with prioritized_customers and summary.
        """
        results = []
        for cust in customers:
            days = int(cust.get("days_since_purchase", 180))
            total_spend = float(cust.get("total_spend", 0))
            total_orders = int(cust.get("total_orders", 1))
            aov = float(cust.get("avg_order_value", total_spend / max(total_orders, 1)))
            name = str(cust.get("name", f"Customer {cust.get('id','')}"))
            cat = str(cust.get("preferred_category", "general"))

            # Value tier
            if total_spend >= 500 or total_orders >= 5:
                value_tier = "high_value"
            elif total_spend >= 150 or total_orders >= 2:
                value_tier = "medium_value"
            else:
                value_tier = "low_value"

            # Lapse tier
            lapse_label = "at_risk_churned"
            lapse_note = "Very long lapse"
            for start, end, label, note in LAPSE_TIERS:
                if start <= days < end:
                    lapse_label = label
                    lapse_note = note
                    break

            # Win-back score (0-100)
            score = self._winback_score(days, total_spend, total_orders, aov)

            # Discount offer
            discount = self._calc_discount(value_tier, lapse_label, max_discount_pct)

            # Email sequence
            seq_template = WINBACK_EMAIL_SEQUENCES.get(value_tier, WINBACK_EMAIL_SEQUENCES["low_value"])
            emails = []
            for email in seq_template:
                emails.append({
                    "send_day": email["day"],
                    "subject": email["subject"].format(name=name.split()[0], brand=brand_name, discount=discount),
                    "hook": email["hook"],
                })

            results.append({
                "customer_id": cust.get("id", ""),
                "name": name,
                "days_since_purchase": days,
                "total_spend_usd": total_spend,
                "total_orders": total_orders,
                "preferred_category": cat,
                "value_tier": value_tier,
                "lapse_tier": lapse_label,
                "lapse_note": lapse_note,
                "winback_score": score,
                "offer_discount_pct": discount,
                "offer_code": f"BACK{discount}",
                "email_sequence": emails,
            })

        results.sort(key=lambda x: x["winback_score"], reverse=True)

        summary = {
            "total_lapsed_customers": len(results),
            "high_priority": sum(1 for r in results if r["winback_score"] >= 65),
            "medium_priority": sum(1 for r in results if 35 <= r["winback_score"] < 65),
            "low_priority": sum(1 for r in results if r["winback_score"] < 35),
            "avg_winback_score": round(sum(r["winback_score"] for r in results) / max(len(results), 1), 1),
            "total_potential_revenue": round(sum(r["total_spend_usd"] * 0.3 for r in results if r["winback_score"] >= 50), 2),
        }

        return {"prioritized_customers": results, "summary": summary}

    @staticmethod
    def _winback_score(days: int, spend: float, orders: int, aov: float) -> int:
        score = 0
        # Recency (closer = higher)
        if days < 120: score += 40
        elif days < 180: score += 30
        elif days < 365: score += 15
        else: score += 5
        # Value
        if spend >= 500: score += 30
        elif spend >= 200: score += 20
        elif spend >= 50: score += 10
        # Frequency
        if orders >= 5: score += 20
        elif orders >= 3: score += 12
        elif orders >= 2: score += 6
        # AOV bonus
        if aov >= 100: score += 10
        return min(score, 100)

    @staticmethod
    def _calc_discount(value_tier: str, lapse_tier: str, max_disc: float) -> int:
        base = {"high_value": max_disc, "medium_value": max_disc * 0.7, "low_value": max_disc * 0.5}
        tier_mult = {"recently_lapsed": 0.6, "moderately_lapsed": 0.8, "long_lapsed": 1.0, "at_risk_churned": 1.0}
        disc = base.get(value_tier, max_disc * 0.5) * tier_mult.get(lapse_tier, 1.0)
        return max(5, min(int(round(disc / 5) * 5), int(max_disc)))
