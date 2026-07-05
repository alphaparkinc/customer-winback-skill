"""
example_usage.py -- Demonstrates the CustomerWinbackClient SDK.
"""
from client import CustomerWinbackClient

def main():
    client = CustomerWinbackClient()

    lapsed = [
        {"id":"C001","name":"Sarah Chen","days_since_purchase":95,"total_orders":8,"total_spend":620,"avg_order_value":77.5,"preferred_category":"beauty"},
        {"id":"C002","name":"Mark Davis","days_since_purchase":210,"total_orders":3,"total_spend":185,"avg_order_value":61.7,"preferred_category":"fitness"},
        {"id":"C003","name":"Emma Wilson","days_since_purchase":420,"total_orders":1,"total_spend":45,"avg_order_value":45,"preferred_category":"fashion"},
        {"id":"C004","name":"James Lee","days_since_purchase":150,"total_orders":5,"total_spend":490,"avg_order_value":98,"preferred_category":"electronics"},
        {"id":"C005","name":"Lisa Park","days_since_purchase":730,"total_orders":2,"total_spend":110,"avg_order_value":55,"preferred_category":"home"},
    ]

    print("[Customer Win-Back Campaign Generator]")
    result = client.run(lapsed, brand_name="GlowStore", max_discount_pct=25)

    s = result["summary"]
    print(f"Total Lapsed: {s['total_lapsed_customers']} | High Priority: {s['high_priority']} | Avg Score: {s['avg_winback_score']}")
    print(f"Potential Revenue Recovery: ${s['total_potential_revenue']:,.2f}")

    print(f"\nPrioritized Customers:")
    for cust in result["prioritized_customers"]:
        print(f"\n  {cust['name']} [{cust['value_tier']}] | Score: {cust['winback_score']} | Lapse: {cust['days_since_purchase']}d ({cust['lapse_tier']})")
        print(f"  Offer: {cust['offer_discount_pct']}% off | Code: {cust['offer_code']}")
        print(f"  Email Sequence ({len(cust['email_sequence'])} emails):")
        for email in cust["email_sequence"][:2]:
            print(f"    Day {email['send_day']}: {email['subject']}")

if __name__ == "__main__":
    main()
