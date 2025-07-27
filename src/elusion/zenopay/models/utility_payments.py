from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class AirtimeService(BaseModel):
    code: Literal["TOP", "NCARD"]
    ref_label: str
    description: str


class ElectricityService(BaseModel):
    code: Literal["LUKU", "TUKUZA"]
    ref_label: str
    description: str


class TVSubscriptionService(BaseModel):
    code: Literal["DSTV", "DSTVBO", "AZAMTV", "STARTIMES", "ZUKU"]
    ref_label: str
    description: str


class InternetService(BaseModel):
    code: Literal["SMILE", "ZUKUFIBER", "TTCL"]
    ref_label: str
    description: str


class GovernmentService(BaseModel):
    code: Literal["GEPG", "ZANMALIPO"]
    ref_label: str
    description: str


class FlightTicketService(BaseModel):
    code: Literal["PW", "COASTAL", "AURIC"]
    ref_label: str
    description: str


class PensionMerchantService(BaseModel):
    code: Literal["UTT", "SELCOMPAY"]
    ref_label: str
    description: str


# Union type for all utility codes
UtilityCode = Literal[
    # Airtime
    "TOP",
    "NCARD",
    # Electricity
    "LUKU",
    "TUKUZA",
    # TV Subscriptions
    "DSTV",
    "DSTVBO",
    "AZAMTV",
    "STARTIMES",
    "ZUKU",
    # Internet
    "SMILE",
    "ZUKUFIBER",
    "TTCL",
    # Government
    "GEPG",
    "ZANMALIPO",
    # Flights & Tickets
    "PW",
    "COASTAL",
    "AURIC",
    # Pensions & Merchants
    "UTT",
    "SELCOMPAY",
]


class NewUtilityPayment(BaseModel):
    transid: str = Field(..., description="Unique transaction ID from client system")
    utilitycode: UtilityCode = Field(..., description="Type of utility to pay")
    utilityref: str = Field(..., description="Customer reference: meter no, card no, phone etc.")
    amount: int = Field(..., gt=0, description="Amount in TZS")
    pin: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$", description="4-digit secure PIN")
    msisdn: str = Field(..., description="Paying customer's mobile number")


class UtilityPaymentResponseData(BaseModel):
    pass


class SelcomResponse(BaseModel):
    reference: str
    transid: str
    resultcode: str
    result: str
    message: str
    data: List[UtilityPaymentResponseData]


class UtilityPaymentResponse(BaseModel):
    status: str
    message: str
    data: SelcomResponse = Field(..., alias="selcom_response")

    @property
    def resultCode(self) -> Optional[str]:
        return self.data.resultcode
