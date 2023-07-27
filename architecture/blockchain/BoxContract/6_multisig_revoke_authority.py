from algosdk.atomic_transaction_composer import *
from algosdk import account
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

# creator_mnemonic = "infant flag husband illness gentle palace eye tilt large reopen current purity enemy depart couch moment gate transfer address diamond vital between unlock able cave"
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

AUTHORITY1_ADDRESS="NBKP3E7M4OVO3SV3FEJQQ2Z2NVMRQMRWS654MMLCKSKXGLRFMF5Z6ACGCA"
AUTHORITY2_ADDRESS="XE36THD3UXASJ4DMF4W3WZV4KCZQZYJR2LJCUHJDHTTLLTUXY22JZ4QK3U"
AUTHORITY3_ADDRESS="54MW2OHJNUOT3ZERNYDWAOLL5ZB2WDQVB42DFAIXVZI53HYF3LBOWZTSYY"
AUTHORITY4_ADDRESS="Z5ZNF7XYPNUPCQGUAUUI3F5UCWPV7KNORRRMR4KPUSFGVQSQO3QYNXQSXA"

def get_method(name: str, js: str) -> Method:
    c = Contract.from_json(js)
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with the name {}".format(name))

def removeApprovedAuthority(client: algod.AlgodClient, app_id: int, toApproveAddress: str):

    sender = msig.address()

    atc = AtomicTransactionComposer()
    signer = MultisigTransactionSigner(msig, [private_key_1, private_key_2])
    sp = client.suggested_params()

    app_args = [
        toApproveAddress
    ]

    with open("./contract.json") as f:
        js = f.read()

    atc.add_method_call(
        app_id=app_id,
        method=get_method('revokeAuthority', js),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=app_args
    )

    result = atc.execute(client, 10)

    print("Transaction id:", result.tx_ids[0])


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address=AUTHORITY1_ADDRESS
    app_id=239796376
    removeApprovedAuthority(algod_client, app_id, address)


if __name__ == "__main__":
    main()