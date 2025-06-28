import asyncio
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_order_id


# Setup
client = ZenoPay()


# Create order (sync)
def create_order():
    with client:
        order = NewOrder(
            order_id=generate_order_id(),
            buyer_email="test@example.com",
            buyer_name="Test User",
            buyer_phone="0781588379",
            amount=1000,
        )
        response = client.orders.sync.create(order)
        return response.results.order_id


# Check status (sync)
def check_status(order_id: str):
    with client:
        response = client.orders.sync.check_status(order_id)
        return response.results


# Check payment (sync)
def check_payment(order_id: str):
    with client:
        return client.orders.sync.check_payment(order_id)


# Wait for payment to succeed (sync)
def wait_for_payment(order_id: str):
    with client:
        return client.orders.sync.wait_for_payment(order_id)


# Create order (async)
async def create_order_async():
    async with client:
        order = NewOrder(
            order_id=generate_order_id(),
            buyer_email="test@example.com",
            buyer_name="Test User",
            buyer_phone="0781588379",
            amount=1000,
            webhook_url="https://example.com/webhook",
            metadata={"key": "value"},
        )
        response = await client.orders.create(order)
        return response.results.order_id


# Check status (async)
async def check_status_async(order_id: str):
    async with client:
        response = await client.orders.check_status(order_id)
        return response.results.data[0].payment_status


# Check payment (async)
async def check_payment_async(order_id: str):
    async with client:
        return await client.orders.check_payment(order_id)


if __name__ == "__main__":
    order_id = create_order()
    status = check_status(order_id)
    is_paid = check_payment(order_id)

    print(f"Order: {order_id}")
    print(f"Status: {status.data[0].payment_status}")
    print(f"Paid: {is_paid}")

    order_content = wait_for_payment(order_id)

    print(f"Order ID: {order_content}")

    # Async usage
    async def async_example():
        order_id = await create_order_async()
        status = await check_status_async(order_id)
        is_paid = await check_payment_async(order_id)

        print(f"Async Order: {order_id}")
        print(f"Async Status: {status}")
        print(f"Async Paid: {is_paid}")

    asyncio.run(async_example())
