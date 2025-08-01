import asyncio
from elusion.zenopay import ZenoPay, Currency
from elusion.zenopay.models.checkout import NewCheckout


# Setup
client = ZenoPay()


# Create checkout session (sync)
def create_checkout():
    with client:
        checkout = NewCheckout(
            buyer_email="test@example.com",
            buyer_name="Test User",
            buyer_phone="06XXXXXXX",
            amount=1000,
            currency=Currency.TZS,
            redirect_url="https://example.com/success",
        )
        response = client.checkout.sync.create(checkout)
        return response.results


# Create checkout session (async)
async def create_checkout_async():
    async with client:
        checkout = NewCheckout(
            buyer_email="async@example.com",
            buyer_name="Async User",
            buyer_phone="06XXXXXXX",
            amount=2000,
            currency=Currency.KES,
            redirect_url="https://example.com/async-success",
        )
        response = await client.checkout.create(checkout)
        return response.results


if __name__ == "__main__":
    # Sync examples
    print("=== Sync Checkout Examples ===")

    checkout_result = create_checkout()
    print(f"Checkout Payment Link: {checkout_result.payment_link}")
    print(f"Transaction Reference: {checkout_result.tx_ref}")
    print()

    # Async examples
    async def async_examples():
        print("=== Async Checkout Examples ===")

        async_result = await create_checkout_async()
        print(f"Async Checkout Link: {async_result.payment_link}")
        print(f"Async TX Ref: {async_result.tx_ref}")

    asyncio.run(async_examples())
