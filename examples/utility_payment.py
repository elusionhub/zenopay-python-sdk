from elusion.zenopay import ZenoPay
from elusion.zenopay.models import NewUtilityPayment
from elusion.zenopay.utils import generate_id

client = ZenoPay()


def pay():
    response = client.utilities.sync.process_payment(
        payment_data=NewUtilityPayment(
            transid=generate_id(prefix="ELUSION_SDK"),
            utilitycode="TOP",  # Airtime top-up
            utilityref="07XXXXXXXX",  # Phone number for airtime
            amount=500,  # 500 TZS
            pin="2025",  # 4-digit PIN
            msisdn="07XXXXXXXX",  # Customer mobile
        )
    )

    response.results.data


if __name__ == "__main__":
    pay()
