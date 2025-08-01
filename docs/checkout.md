# ZenoPay Checkout

Create secure payment checkout sessions for online payments with support for multiple currencies and redirect handling.

## Quick Start

```python
from elusion.zenopay import ZenoPay, Currency
from elusion.zenopay.models.checkout import NewCheckout

client = ZenoPay()

response = client.checkout.sync.create(
    checkout_data=NewCheckout(
        buyer_email="customer@example.com",
        buyer_name="John Doe",
        buyer_phone="06XXXXXXX",
        amount=1000,
        currency=Currency.TZS,
        redirect_url="https://example.com/success"
    )
)

payment_link = response.results.payment_link
tx_ref = response.results.tx_ref
```

## Supported Currencies

### Major International Currencies

- `USD` - US Dollar 🇺🇸
- `EUR` - Euro 🇪🇺
- `GBP` - British Pound 🇬🇧
- `CAD` - Canadian Dollar 🇨🇦
- `AUD` - Australian Dollar 🇦🇺
- `CHF` - Swiss Franc 🇨🇭

### African Currencies

- `TZS` - Tanzanian Shilling 🇹🇿
- `KES` - Kenyan Shilling 🇰🇪
- `UGX` - Ugandan Shilling 🇺🇬
- `NGN` - Nigerian Naira 🇳🇬
- `ZAR` - South African Rand 🇿🇦

### Middle East & Asia

- `SAR` - Saudi Riyal 🇸🇦
- `AED` - Emirati Dirham 🇦🇪
- `INR` - Indian Rupee 🇮🇳
- `CNY` - Chinese Yuan 🇨🇳
- `JPY` - Japanese Yen 🇯🇵

## Parameters

```python
NewCheckout(
    buyer_email="customer@example.com",      # Customer's email address
    buyer_name="John Doe",                   # Customer's full name
    buyer_phone="06XXXXXXX",                # Customer's phone number
    amount=1000,                             # Amount in smallest currency unit
    currency=Currency.TZS,                   # Currency code
    redirect_url="https://example.com/success"  # Post-payment redirect URL
)
```

## Examples

### Basic Checkout

```python
# Simple checkout with minimal data
checkout = NewCheckout(
    buyer_email="customer@example.com",
    buyer_name="Jane Smith",
    buyer_phone="06XXXXXXX",
    amount=5000,
    currency=Currency.USD,
    redirect_url="https://mystore.com/success"
)
```

### E-commerce Checkout

```python
# E-commerce checkout for product purchase
checkout = NewCheckout(
    buyer_email="shopper@example.com",
    buyer_name="Mike Johnson",
    buyer_phone="06XXXXXXX",
    amount=25000,
    currency=Currency.TZS,
    redirect_url="https://mystore.com/order-complete"
)
```

### Subscription Checkout

```python
# Subscription payment
checkout = NewCheckout(
    buyer_email="subscriber@example.com",
    buyer_name="Sarah Wilson",
    buyer_phone="06XXXXXXX",
    amount=2999,
    currency=Currency.KES,
    redirect_url="https://myapp.com/dashboard"
)
```

### Multi-currency Support

```python
# USD checkout for international customers
usd_checkout = NewCheckout(
    buyer_email="global@example.com",
    buyer_name="Alex Chen",
    buyer_phone="06XXXXXXX",
    amount=50,  # $0.50 USD
    currency=Currency.USD,
    redirect_url="https://globalstore.com/success"
)

# Local currency checkout
tzs_checkout = NewCheckout(
    buyer_email="local@example.com",
    buyer_name="Amara Kofi",
    buyer_phone="06XXXXXXX",
    amount=1200,  # 1,200 TZS
    currency=Currency.TZS,
    redirect_url="https://localstore.com/success"
)
```

## Async Usage

```python
# Async checkout creation
response = await client.checkout.create(checkout_data=checkout)
payment_link = response.results.payment_link
tx_ref = response.results.tx_ref

# Redirect customer to payment_link
print(f"Please complete payment at: {payment_link}")
print(f"Transaction reference: {tx_ref}")
```

## Response Handling

```python
# Create checkout
response = client.checkout.sync.create(checkout_data=checkout)

# Get payment link and transaction reference
payment_link = response.results.payment_link
transaction_ref = response.results.tx_ref

# Redirect customer to payment page
print(f"Payment Link: {payment_link}")
print(f"Transaction ID: {transaction_ref}")

# Use transaction_ref to track payment status
```

## Best Practices

1. **Always use HTTPS** for redirect URLs
2. **Store transaction reference** for payment tracking
3. **Handle payment failures** gracefully with retry mechanisms
4. **Validate redirect URLs** before creating checkout sessions
5. **Use appropriate currency** for your target market
