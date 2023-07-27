from algosdk.atomic_transaction_composer import *
from algosdk import account, transaction
from pyteal import *
from algosdk.abi import Method, Contract

private_key_1 = "VZtHXj4T2DT2atlThLRuOgPE0n+bj9sO6e/6STgm3Nqrr3giY49gyUtq/fJ5mIPp9S8clJfgy2QhgnBkybRvrg=="
private_key_2 = "v1NEi7llgXaH66aofgHv+/8RW3MsOUmqneWc/Tm97n+IsGQHQS4zOZ6l+p9ezvUDMdxxmmua9TIPXeVfdLjhwg=="
private_key_3 = "nOewRj9MCGANg7oSlpqc6YO+2zl+2SBzp70/W4MlEka9EUkqdHXusgjGprC0u2C3A3HgBeP1AolBuxzUnlwYmw=="
private_key_4 = "9Qekcr0Ba5DV3gm9XrH267zy3xElYlAvv8QArpgEqfMzVNyMgn1/ZBIAuHNkZXusBB3GPeufTH5Z8vNiFvHGog=="

account_1 = account.address_from_private_key(private_key_1)
account_2 = account.address_from_private_key(private_key_2)
account_3 = account.address_from_private_key(private_key_3)
account_4 = account.address_from_private_key(private_key_4)

version = 1  # multisig version
threshold = 2  # how many signatures are necessary
msig = transaction.Multisig(version, threshold, [account_1, account_2])

print("Multisig Address: ", msig.address())

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

DATAOWNER_ADDRESS='SVCAKVYOAWOUKTB4YK3DQH2SCEMAKZ3OVLXIBUANDMJNOI7COXUO34NWG4'

def get_method(name: str, js: str) -> Method:
    c = Contract.from_json(js)
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with the name {}".format(name))


def addApprovedReader(client: algod.AlgodClient, app_id: int, toApproveAddress: str):

    sender = msig.address()

    atc = AtomicTransactionComposer()
    signer =  MultisigTransactionSigner(msig, [private_key_1, private_key_2])
    sp = client.suggested_params()

    app_args = [
        toApproveAddress
    ]

    with open("./contract.json") as f:
        js = f.read()

    atc.add_method_call(
        app_id=app_id,
        method=get_method('revokeDataOwner', js),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=app_args
    )

    result = atc.execute(client, 10)

    print("Transaction id:", result.tx_ids[0])


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address=DATAOWNER_ADDRESS
    app_id=239745672
    addApprovedReader(algod_client, app_id, address)


if __name__ == "__main__":
    main()