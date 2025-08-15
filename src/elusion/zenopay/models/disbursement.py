from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field
from elusion.zenopay.models.common import UtilityCodes


class NewDisbursement(BaseModel):
    transid: str = Field(..., description="Unique transaction ID (e.g., UUID) to prevent duplication.")
    utilitycode: str = Field(default=UtilityCodes.CASHIN, description='Set to "CASHIN" for disbursements.')
    utilityref: str = Field(..., description="Mobile number to receive the funds (e.g., 0744963858).")
    amount: int = Field(..., description="Amount to send in Tanzanian Shillings (TZS).")
    pin: str = Field(
        ...,
        description="4-digit wallet PIN to authorize the transaction.",
        pattern=r"^\d{4}$"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"transid": "7pbBX-lnnASw-erwnn-nrrr09AZ", "utilitycode": "CASHIN", "utilityref": "07XXXXXXXX", "amount": 1000, "pin": 0000}
        }
    )


class ZenoPayResponse(BaseModel):
    reference: str
    transid: str
    resultcode: str
    result: str
    message: str
    data: List[Dict[str, Any]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reference": "0949694808",
                "transid": "7pbBXlnnASwerdsadasdwnnnrrr09AZ",
                "resultcode": "000",
                "result": "SUCCESS",
                "message": "\nMpesa\nTo JOHN DOE(2557XXXXXXXX)\nFrom ZENO\nAmount 1,000.00\n\nReference 0949694808\n26/06/2025 7:21:24 PM",
                "data": [],
            }
        }
    )


class DisbursementSuccessResponse(BaseModel):
    status: str
    message: str
    fee: int
    amount_sent_to_customer: int
    total_deducted: int
    new_balance: str
    zenopay_response: ZenoPayResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Wallet Cashin processed successfully.",
                "fee": 1500,
                "amount_sent_to_customer": 3000,
                "total_deducted": 4500,
                "new_balance": "62984034.00",
                "zenopay_response": {
                    "reference": "0949694808",
                    "transid": "7pbBXlnnASwerdsadasdwnnnrrr09AZ",
                    "resultcode": "000",
                    "result": "SUCCESS",
                    "message": "\nMpesa\nTo JOHN DOE(2557XXXXXXXX)\nFrom ZENO\nAmount 1,000.00\n\nReference 0949694808\n26/06/2025 7:21:24 PM",
                    "data": [],
                },
            }
        }
    )
