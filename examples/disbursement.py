from elusion.zenopay import ZenoPay
from elusion.zenopay.models.disbursement import NewDisbursement, UtilityCodes
from elusion.zenopay.utils import generate_id

client = ZenoPay()


def disburse():
    response = client.disbursements.sync.disburse(
        disbursement_data=NewDisbursement(amount=5000, pin="0000", transid=generate_id(), utilitycode=UtilityCodes.CASHIN, utilityref="07XXXXXXXX")
    )
    return response.results.zenopay_response.result


if __name__ == "__main__":
    disburse()
