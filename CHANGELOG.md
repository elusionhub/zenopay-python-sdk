# Changelog

All notable changes to the ZenoPay Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-07-27

### Added

- **Utility Payments API**: Complete utility bill payment functionality
- New `UtilityPaymentsService` with sync/async support
- Support for 22+ utility services across 6 categories:
  - **Airtime & Top-up**: `TOP`, `NCARD`
  - **Electricity**: `LUKU`, `TUKUZA`
  - **TV Subscriptions**: `DSTV`, `DSTVBO`, `AZAMTV`, `STARTIMES`, `ZUKU`
  - **Internet**: `SMILE`, `ZUKUFIBER`, `TTCL`
  - **Government**: `GEPG`, `ZANMALIPO`
  - **Flights & Tickets**: `PW`, `COASTAL`, `AURIC`
  - **Pensions & Merchants**: `UTT`, `SELCOMPAY`
- New `NewUtilityPayment` model with validation
- Utility service type models: `AirtimeService`, `ElectricityService`, etc.
- Client access via `client.utilities.sync.process_payment()` and `client.utilities.process_payment()`

## [0.2.0] - 2025-06-27

### Added

- **Disbursements API**: Mobile money disbursement functionality
- New `DisbursementService` with sync/async support
- `NewDisbursement` model with validation
- Support for mobile money cash-in operations (`UtilityCodes.CASHIN`)
- Client access via `client.disbursements.sync.disburse()` and `client.disbursements.disburse()`

## [0.1.0] - 2025-06-15

### Added

- **Orders API**: Complete payment order management
- **Webhook System**: Event handling for payment status updates
- Flask and FastAPI webhook integration examples
- Order operations:
  - Create payment orders
  - Check payment status
  - Check payment completion (boolean)
  - Wait for payment completion with polling
- Enhanced error handling with specific exception types
- Metadata support in order creation
- Context manager implementation for resource management

## [0.0.1] - 2025-06-01

### Added

- Initial release of ZenoPay Python SDK
- Project structure and foundation
- Environment-based configuration
- HTTP client with async/sync support
- Pydantic models for type safety
- Base service architecture
- Comprehensive error handling framework

---

## Features by Version

| Version   | Core Features                                 |
| --------- | --------------------------------------------- |
| **0.3.0** | Orders + Disbursements + **Utility Payments** |
| **0.2.0** | Orders + **Disbursements**                    |
| **0.1.0** | **Orders + Webhooks**                         |
| **0.0.1** | **Foundation**                                |

## Support

- **GitHub**: [zenopay-python-sdk](https://github.com/elusionhub/zenopay-python-sdk)
- **Issues**: [Report bugs](https://github.com/elusionhub/zenopay-python-sdk/issues)
- **Email**: elusion.lab@gmail.com
