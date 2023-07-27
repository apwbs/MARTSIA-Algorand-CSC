from algosdk.atomic_transaction_composer import *
from algosdk import account, transaction
from pyteal import *
from algosdk.abi import Method, Contract
from decouple import config

APP_ID = config('APPLICATION_ID_MESSAGES')
DATAOWNER_ADDRESS = config('DATAOWNER_ADDRESS')
pk_attribute_certifier_1 = config('CERTIFIER_PRIVATEKEY1')
pk_attribute_certifier_2 = config('CERTIFIER_PRIVATEKEY2')
pk_attribute_certifier_3 = config('CERTIFIER_PRIVATEKEY3')
pk_attribute_certifier_4 = config('CERTIFIER_PRIVATEKEY4')

account_1 = account.address_from_private_key(pk_attribute_certifier_1)
account_2 = account.address_from_private_key(pk_attribute_certifier_2)
account_3 = account.address_from_private_key(pk_attribute_certifier_3)
account_4 = account.address_from_private_key(pk_attribute_certifier_4)

version = 1  # multisig version
threshold = 2  # how many signatures are necessary
msig = transaction.Multisig(version, threshold, [account_1, account_2])

print("Multisig Address: ", msig.address())

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}


def get_method(name: str, js: str) -> Method:
    c = Contract.from_json(js)
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with the name {}".format(name))


def addApprovedReader(client: algod.AlgodClient, app_id: int, toApproveAddress: str):
    sender = msig.address()

    atc = AtomicTransactionComposer()
    signer = MultisigTransactionSigner(msig, [pk_attribute_certifier_1, pk_attribute_certifier_2])
    sp = client.suggested_params()

    app_args = [
        toApproveAddress
    ]

    with open("./contract.json") as f:
        js = f.read()

    atc.add_method_call(
        app_id=app_id,
        method=get_method('approveDataOwner', js),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=app_args
    )

    result = atc.execute(client, 10)

    print("Transaction id:", result.tx_ids[0])


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address = DATAOWNER_ADDRESS
    app_id = APP_ID
    addApprovedReader(algod_client, app_id, address)


if __name__ == "__main__":
    main()
