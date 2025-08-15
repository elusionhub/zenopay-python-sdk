# ZenoPay Python SDK

Modern Python SDK for ZenoPay payment API with async/sync support, order management, disbursements, and checkout sessions.

**NEW in v0.4.0**: Checkout API now available! Create secure payment checkout sessions with multi-currency support and redirect handling.

**v0.3.0**: Utility Payments API - Pay for airtime, electricity, TV subscriptions, internet, government bills, and more.

## Installation

```bash
pip install zenopay-sdk
```

## Quick Start

```python
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_id

# Initialize client (uses environment variables)
client = ZenoPay()

# Create order (sync)
with client:
    order = NewOrder(
        order_id=generate_id(),
        buyer_email="customer@example.com",
        buyer_name="John Doe",
        buyer_phone="07XXXXXXXX",
        amount=1000
    )
    response = client.orders.sync.create(order)
    print(f"Order ID: {response.results.order_id}")
```

## Configuration

### Environment Variables

```bash
export ZENOPAY_API_KEY="your_api_key"
```

### Code Configuration

```python
client = ZenoPay(
    api_key="your_api_key",
    timeout=30.0
)
```

## Checkout API

### Create Checkout Sessions

```python
from elusion.zenopay import ZenoPay, Currency
from elusion.zenopay.models.checkout import NewCheckout

client = ZenoPay()

# Synchronous checkout
def create_checkout():
    with client:
        checkout = NewCheckout(
            buyer_email="customer@example.com",
            buyer_name="John Doe",
            buyer_phone="0781588379",
            amount=1000,
            currency=Currency.TZS,
            redirect_url="https://yourwebsite.com/success"
        )
        response = client.checkout.sync.create(checkout)
        return response.results

# Asynchronous checkout
async def create_checkout_async():
    async with client:
        checkout = NewCheckout(
            buyer_email="customer@example.com",
            buyer_name="John Doe",
            buyer_phone="0781588379",
            amount=2000,
            currency=Currency.USD,
            redirect_url="https://yourwebsite.com/success"
        )
        response = await client.checkout.create(checkout)
        return response.results

# Usage example
if __name__ == "__main__":
    # Sync checkout
    checkout_result = create_checkout()
    print(f"Payment Link: {checkout_result.payment_link}")
    print(f"Transaction Reference: {checkout_result.tx_ref}")
```

### Supported Currencies

```python
from elusion.zenopay import Currency

# Major international currencies
Currency.USD  # US Dollar
Currency.EUR  # Euro
Currency.GBP  # British Pound
Currency.CAD  # Canadian Dollar
Currency.AUD  # Australian Dollar
Currency.CHF  # Swiss Franc

# African currencies
Currency.TZS  # Tanzanian Shilling
Currency.KES  # Kenyan Shilling
Currency.UGX  # Ugandan Shilling
Currency.NGN  # Nigerian Naira
Currency.ZAR  # South African Rand

# Middle East & Asia
Currency.SAR  # Saudi Riyal
Currency.AED  # Emirati Dirham
Currency.INR  # Indian Rupee
Currency.CNY  # Chinese Yuan
Currency.JPY  # Japanese Yen
```

## Orders API

### Synchronous Operations

```python
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_id

client = ZenoPay()

# Create order
def create_order():
    with client:
        order = NewOrder(
            order_id=generate_id(),
            buyer_email="test@example.com",
            buyer_name="Test User",
            buyer_phone="07XXXXXXXX",
            amount=1000,
        )
        response = client.orders.sync.create(order)
        return response.results.order_id

# Check status
def check_status(order_id: str):
    with client:
        response = client.orders.sync.check_status(order_id)
        return response.results

# Check if paid
def check_payment(order_id: str):
    with client:
        return client.orders.sync.check_payment(order_id)

# Wait for payment completion
def wait_for_payment(order_id: str):
    with client:
        return client.orders.sync.wait_for_payment(order_id)

# Usage example
if __name__ == "__main__":
    order_id = create_order()
    status = check_status(order_id)
    is_paid = check_payment(order_id)

    print(f"Order: {order_id}")
    print(f"Status: {status.data[0].payment_status}")
    print(f"Paid: {is_paid}")

    order_content = wait_for_payment(order_id)
    print(f"Order completed: {order_content}")
```

### Asynchronous Operations

```python
import asyncio
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_id

client = ZenoPay()

# Create order (async)
async def create_async():
    async with client:
        order = NewOrder(
            order_id=generate_id(),
            buyer_email="test@example.com",
            buyer_name="Test User",
            buyer_phone="07XXXXXXXX",
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

# Usage example
async def async_example():
    order_id = await create_async()
    status = await check_status_async(order_id)
    is_paid = await check_payment_async(order_id)

    print(f"Async Order: {order_id}")
    print(f"Async Status: {status}")
    print(f"Async Paid: {is_paid}")

asyncio.run(async_example())
```

## Disbursements API

### Mobile Money Disbursements

```python
from elusion.zenopay import ZenoPay
from elusion.zenopay.models.disbursement import NewDisbursement, UtilityCodes
from elusion.zenopay.utils import generate_id

client = ZenoPay()

def disburse():
    response = client.disbursements.sync.disburse(
        disbursement_data=NewDisbursement(
            amount=5000,
            pin="0000",  # Your ZenoPay PIN
            transid=generate_id(),
            utilitycode=UtilityCodes.CASHIN,
            utilityref="07XXXXXXXX"  # Phone number
        )
    )
    return response.results.zenopay_response.result

# Usage
if __name__ == "__main__":
    result = disburse()
    print(f"Disbursement result: {result}")
```

### Available Utility Codes

```python
from elusion.zenopay.models.disbursement import UtilityCodes

# Available disbursement types
UtilityCodes.CASHIN      # Mobile money cash-in
# Add other available codes as needed
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
from elusion.zenopay import ZenoPay

app = Flask(__name__)
client = ZenoPay()

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
from elusion.zenopay import ZenoPay

app = FastAPI()
client = ZenoPay()

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
    ZenoPayNetworkError,
    ZenoPayAuthenticationError
)

try:
    with client:
        response = client.orders.sync.create(order)
except ZenoPayValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.validation_errors}")
except ZenoPayAuthenticationError as e:
    print(f"Authentication error: {e.message}")
except ZenoPayNetworkError as e:
    print(f"Network error: {e.message}")
except ZenoPayError as e:
    print(f"General error: {e.message}")
```

## Models

### Checkout Models

```python
from elusion.zenopay import Currency
from elusion.zenopay.models.checkout import NewCheckout

# Create checkout session
checkout = NewCheckout(
    buyer_email="customer@example.com",
    buyer_name="John Doe",
    buyer_phone="0781588379",
    amount=1000,
    currency=Currency.TZS,
    redirect_url="https://yourwebsite.com/success"
)
```

### Order Models

```python
from elusion.zenopay.models.order import NewOrder
from elusion.zenopay.utils import generate_id

# Create order with all fields
order = NewOrder(
    order_id=generate_id(),
    buyer_email="customer@example.com",
    buyer_name="John Doe",
    buyer_phone="07XXXXXXXX",
    amount=1000,
    webhook_url="https://example.com/webhook",
    metadata={
        "product_id": "12345",
        "campaign": "summer_sale"
    }
)

# Minimal order
order = NewOrder(
    order_id=generate_id(),
    buyer_email="customer@example.com",
    buyer_name="John Doe",
    buyer_phone="07XXXXXXXX",
    amount=1000
)
```

### Disbursement Models

```python
from elusion.zenopay.models.disbursement import NewDisbursement, UtilityCodes
from elusion.zenopay.utils import generate_id

# Mobile money disbursement
disbursement = NewDisbursement(
    amount=5000,
    pin="0000",  # Your ZenoPay PIN
    transid=generate_id(),
    utilitycode=UtilityCodes.CASHIN,
    utilityref="07XXXXXXXX"  # Phone number
)
```

### Response Models

```python
# Checkout response
checkout_response = client.checkout.sync.create(checkout)
print(f"Payment Link: {checkout_response.results.payment_link}")
print(f"Transaction Reference: {checkout_response.results.tx_ref}")

# Order creation response
response = client.orders.sync.create(order)
print(f"Order ID: {response.results.order_id}")

# Status check response
status = client.orders.sync.check_status(order_id)
print(f"Payment Status: {status.results.data[0].payment_status}")

# Disbursement response
response = client.disbursements.sync.disburse(disbursement_data)
print(f"Result: {response.results.zenopay_response.result}")
```

## API Reference

### Checkout Operations

| Method          | Sync                            | Async                            | Description                     |
| --------------- | ------------------------------- | -------------------------------- | ------------------------------- |
| Create Checkout | `client.checkout.sync.create()` | `await client.checkout.create()` | Create payment checkout session |

### Order Operations

| Method           | Sync                                    | Async                                    | Description                |
| ---------------- | --------------------------------------- | ---------------------------------------- | -------------------------- |
| Create Order     | `client.orders.sync.create()`           | `await client.orders.create()`           | Create new payment order   |
| Check Status     | `client.orders.sync.check_status()`     | `await client.orders.check_status()`     | Check order payment status |
| Check Payment    | `client.orders.sync.check_payment()`    | `await client.orders.check_payment()`    | Returns boolean if paid    |
| Wait for Payment | `client.orders.sync.wait_for_payment()` | `await client.orders.wait_for_payment()` | Poll until completed       |

### Disbursement Operations

| Method   | Sync                                   | Async                                   | Description             |
| -------- | -------------------------------------- | --------------------------------------- | ----------------------- |
| Disburse | `client.disbursements.sync.disburse()` | `await client.disbursements.disburse()` | Send money disbursement |

### Webhook Events

| Event     | Handler Method                           | Description        |
| --------- | ---------------------------------------- | ------------------ |
| COMPLETED | `client.webhooks.on_payment_completed()` | Payment successful |
| FAILED    | `client.webhooks.on_payment_failed()`    | Payment failed     |
| PENDING   | `client.webhooks.on_payment_pending()`   | Payment initiated  |
| CANCELLED | `client.webhooks.on_payment_cancelled()` | Payment cancelled  |

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
client = ZenoPay(api_key=os.getenv('ZENOPAY_API_KEY'))
```

### Generate Unique Order IDs

Always use the built-in utility to generate unique order IDs:

```python
from elusion.zenopay.utils import generate_id

order_id = generate_id()
```

## Support

- **GitHub**: [zenopay-python-sdk](https://github.com/elusionhub/zenopay-python-sdk)
- **Issues**: [Report bugs](https://github.com/elusionhub/zenopay-python-sdk/issues)
- **Email**: elusion.lab@gmail.com

## License

MIT License - see [LICENSE](LICENSE) file for details.
