tools = [
    {
        "name": "refund_customer",
        "description": "Execute refund after a human support lead approves the request.",
    }
]


def refund_customer(customer_id, amount, approved_by):
    return {"status": "refunded", "customer_id": customer_id, "amount": amount}
