# ZenoPay Python SDK

Modern Python SDK for ZenoPay payment API with async/sync support and webhook handling.

## Installation

```bash
pip install zenopay-sdk
```

## Quick Start

```python
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder

# Initialize client
client = ZenoPay(account_id="your_account_id")

# Create order (sync)
with client:
    order = NewOrder(
        buyer_email="customer@example.com",
        buyer_name="John Doe",
        buyer_phone="0700000000",
        amount=1000
    )
    response = client.orders.sync.create(order)
    print(f"Order ID: {response.data.order_id}")
```

## Configuration

### Environment Variables

```bash
export ZENOPAY_ACCOUNT_ID="your_account_id"
export ZENOPAY_API_KEY="your_api_key"        # Optional
export ZENOPAY_SECRET_KEY="your_secret_key"  # Optional
```

### Code Configuration

```python
client = ZenoPay(
    account_id="your_account_id",
    api_key="your_api_key",
    secret_key="your_secret_key",
    timeout=30.0
)
```

## API Usage

### Synchronous Operations

```python
# Create order
with client:
    order_data = {
        "buyer_email": "test@example.com",
        "buyer_name": "Test User",
        "buyer_phone": "0700000000",
        "amount": 5000,
        "webhook_url": "https://yoursite.com/webhook"
    }
    response = client.orders.sync.create(order_data)
    order_id = response.data.order_id

# Check status
with client:
    status = client.orders.sync.get_status(order_id)
    print(f"Payment status: {status.data.payment_status}")

# Check if paid
with client:
    is_paid = client.orders.sync.check_payment(order_id)
    print(f"Paid: {is_paid}")

# Wait for payment
with client:
    try:
        completed = client.orders.sync.wait_for_payment(order_id, timeout=300)
        print("Payment completed!")
    except TimeoutError:
        print("Payment timeout")
```

### Asynchronous Operations

```python
import asyncio

async def create_payment():
    async with client:
        order_data = {
            "buyer_email": "test@example.com",
            "buyer_name": "Test User",
            "buyer_phone": "0700000000",
            "amount": 5000
        }

        # Create order
        response = await client.orders.create(order_data)
        order_id = response.data.order_id

        # Check status
        status = await client.orders.get_status(order_id)
        print(f"Status: {status.data.payment_status}")

        # Wait for completion
        try:
            completed = await client.orders.wait_for_payment(order_id)
            print("Payment completed!")
        except TimeoutError:
            print("Payment timeout")

asyncio.run(create_payment())
```

## Webhook Handling

### Basic Setup

```python
# Setup handlers
def payment_completed(event):
    order_id = event.payload.order_id
    reference = event.payload.reference
    print(f"Payment completed: {order_id} - {reference}")

def payment_failed(event):
    order_id = event.payload.order_id
    print(f"Payment failed: {order_id}")

# Register handlers
client.webhooks.on_payment_completed(payment_completed)
client.webhooks.on_payment_failed(payment_failed)

# Process webhook
webhook_data = '{"order_id":"123","payment_status":"COMPLETED","reference":"REF123"}'
response = client.webhooks.process_webhook_request(webhook_data)
```

### Flask Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
client = ZenoPay(account_id="your_account_id")

def handle_completed_payment(event):
    order_id = event.payload.order_id
    # Update database, send emails, etc.
    print(f"Order {order_id} completed")

client.webhooks.on_payment_completed(handle_completed_payment)

@app.route('/zenopay/webhook', methods=['POST'])
def webhook():
    raw_data = request.data.decode('utf-8')
    response = client.webhooks.process_webhook_request(raw_data)
    return jsonify({'status': response.status})

if __name__ == '__main__':
    app.run()
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request

app = FastAPI()
client = ZenoPay(account_id="your_account_id")

def handle_completed_payment(event):
    order_id = event.payload.order_id
    print(f"Order {order_id} completed")

client.webhooks.on_payment_completed(handle_completed_payment)

@app.post("/zenopay/webhook")
async def webhook(request: Request):
    raw_data = await request.body()
    raw_data_str = raw_data.decode('utf-8')
    response = client.webhooks.process_webhook_request(raw_data_str)
    return {'status': response.status}
```

## Error Handling

```python
from elusion.zenopay.exceptions import (
    ZenoPayError,
    ZenoPayValidationError,
    ZenoPayNetworkError
)

try:
    with client:
        response = client.orders.sync.create(order_data)
except ZenoPayValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.validation_errors}")
except ZenoPayNetworkError as e:
    print(f"Network error: {e.message}")
except ZenoPayError as e:
    print(f"General error: {e.message}")
```

## Order Models

### Creating Orders

```python
from elusion.zenopay.models.order import NewOrder

# Using model
order = NewOrder(
    buyer_email="customer@example.com",
    buyer_name="John Doe",
    buyer_phone="0700000000",
    amount=1000,
    webhook_url="https://yoursite.com/webhook",
    metadata={
        "product_id": "12345",
        "campaign": "summer_sale"
    }
)

# Using dictionary
order_data = {
    "buyer_email": "customer@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0700000000",
    "amount": 1000
}
```

### Response Models

```python
# Order creation response
response = client.orders.sync.create(order)
print(f"Order ID: {response.data.order_id}")
print(f"Status: {response.data.status}")
print(f"Message: {response.data.message}")

# Status check response
status = client.orders.sync.get_status(order_id)
print(f"Payment Status: {status.data.payment_status}")
print(f"Order ID: {status.data.order_id}")
```

## API Reference

### Order Operations

| Method           | Sync                                    | Async                                    | Description                |
| ---------------- | --------------------------------------- | ---------------------------------------- | -------------------------- |
| Create Order     | `client.orders.sync.create()`           | `await client.orders.create()`           | Create new payment order   |
| Get Status       | `client.orders.sync.get_status()`       | `await client.orders.get_status()`       | Check order payment status |
| Check Payment    | `client.orders.sync.check_payment()`    | `await client.orders.check_payment()`    | Returns boolean if paid    |
| Wait for Payment | `client.orders.sync.wait_for_payment()` | `await client.orders.wait_for_payment()` | Poll until completed       |

### Webhook Events

| Event     | Handler Method                           | Description        |
| --------- | ---------------------------------------- | ------------------ |
| COMPLETED | `client.webhooks.on_payment_completed()` | Payment successful |
| FAILED    | `client.webhooks.on_payment_failed()`    | Payment failed     |
| PENDING   | `client.webhooks.on_payment_pending()`   | Payment initiated  |
| CANCELLED | `client.webhooks.on_payment_cancelled()` | Payment cancelled  |

## Testing

```python
# Create test webhook
test_event = client.webhooks.create_test_webhook("test-order-123", "COMPLETED")
response = client.webhooks.handle_webhook(test_event)
print(f"Test response: {response.status}")
```

## Best Practices

### Context Managers

Always use context managers for proper resource cleanup:

```python
# Sync
with client:
    response = client.orders.sync.create(order)

# Async
async with client:
    response = await client.orders.create(order)
```

### Error Handling

Handle specific exceptions for better error management:

```python
try:
    with client:
        response = client.orders.sync.create(order)
except ZenoPayValidationError:
    # Handle validation errors
    pass
except ZenoPayNetworkError:
    # Handle network issues
    pass
```

### Environment Configuration

Use environment variables for sensitive configuration:

```python
# Don't hardcode credentials
client = ZenoPay(account_id=os.getenv('ZENOPAY_ACCOUNT_ID'))
```

## Support

- **GitHub**: [zenopay-python-sdk](https://github.com/elusionhub/zenopay-python-sdk)
- **Issues**: [Report bugs](https://github.com/elusionhub/zenopay-python-sdk/issues)
- **Email**: elusion.lab@gmail.com

## License

MIT License - see [LICENSE](LICENSE) file for details.
