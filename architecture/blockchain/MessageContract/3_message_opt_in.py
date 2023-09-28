from algosdk.atomic_transaction_composer import *
from pyteal import *

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

DATAOWNER_ADDRESS='SVCAKVYOAWOUKTB4YK3DQH2SCEMAKZ3OVLXIBUANDMJNOI7COXUO34NWG4'
DATAOWNER_PRIVATEKEY='8iTtNZ9wCphZUYjQrE8r3SHcSDb7r6xBr0Gn9Avm4UCVRAVXDgWdRUw8wrY4H1IRGAVnbqrugNANGxLXI+J16A=='

def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address=DATAOWNER_ADDRESS
    private_key=DATAOWNER_PRIVATEKEY
    app_id=239586147

    txn = transaction.ApplicationOptInTxn(
        sender=address,
        index=app_id,
        sp=algod_client.suggested_params(),
    )
    signedTxn = txn.sign(private_key)
    algod_client.send_transaction(signedTxn)
    transaction.wait_for_confirmation(algod_client, signedTxn.get_txid())


if __name__ == "__main__":
    main()