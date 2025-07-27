# ZenoPay Utility Payments

Process payments for utilities including airtime, electricity, TV subscriptions, internet, government bills, and more.

## Quick Start

```python
from elusion.zenopay import ZenoPay
from elusion.zenopay.models import NewUtilityPayment
from elusion.zenopay.utils import generate_id

client = ZenoPay()

response = client.utilities.sync.process_payment(
    payment_data=NewUtilityPayment(
        transid=generate_id(prefix="ELUSION_SDK"),
        utilitycode="TOP",
        utilityref="0744963858",
        amount=500,
        pin="2025",
        msisdn="0744963858"
    )
)

result = response.results.data
```

## Supported Utilities

### Airtime & Top-up

- `TOP` - Prepaid Airtime (Mobile Number)
- `NCARD` - N-Card Top Up (Card Number)

### Electricity

- `LUKU` - Electricity LUKU (Meter Number)
- `TUKUZA` - Electricity TUKUZA (Meter Number)

### TV Subscriptions

- `DSTV` - DSTV Subscriptions (Smartcard Number)
- `DSTVBO` - DSTV Box Office (Smartcard Number)
- `AZAMTV` - AZAMTV Subscriptions (Smartcard Number)
- `STARTIMES` - StarTimes (Customer ID/Card Number)
- `ZUKU` - ZUKU TV (Account Number)

### Internet

- `SMILE` - Smile 4G (Account Number)
- `ZUKUFIBER` - ZUKU Fiber Internet (Account Number)
- `TTCL` - TTCL Broadband (Mobile Number)

### Government

- `GEPG` - GEPG Payments (Control Number)
- `ZANMALIPO` - Zanzibar Gov Payments (Control Number)

### Flights & Tickets

- `PW` - Precision Air (Booking Reference)
- `COASTAL` - Coastal Aviation (Booking Reference)
- `AURIC` - Auric Air (Booking Reference)

### Pensions & Merchants

- `UTT` - UTT Amis (Account Number)
- `SELCOMPAY` - Selcom/Masterpass Merchant (Account Number)

## Parameters

```python
NewUtilityPayment(
    transid="UNIQUE_TRANSACTION_ID",     # Unique transaction ID
    utilitycode="TOP",                   # Utility service code
    utilityref="0744963858",             # Customer reference number
    amount=500,                          # Amount in TZS
    pin="2025",                          # 4-digit PIN
    msisdn="0744963858"                  # Customer mobile number
)
```

## Examples

### Airtime

```python
# Buy airtime
payment = NewUtilityPayment(
    transid=generate_id(prefix="AIRTIME"),
    utilitycode="TOP",
    utilityref="0744963858",
    amount=1000,
    pin="2025",
    msisdn="0744963858"
)
```

### Electricity

```python
# Pay electricity bill
payment = NewUtilityPayment(
    transid=generate_id(prefix="LUKU"),
    utilitycode="LUKU",
    utilityref="01234567891",
    amount=50000,
    pin="2025",
    msisdn="0744963858"
)
```

### TV Subscription

```python
# Pay DSTV subscription
payment = NewUtilityPayment(
    transid=generate_id(prefix="DSTV"),
    utilitycode="DSTV",
    utilityref="01234567891",
    amount=25000,
    pin="2025",
    msisdn="0744963858"
)
```

## Async Usage

```python
# Async payment
response = await client.utilities.process_payment(payment_data=payment)
```
