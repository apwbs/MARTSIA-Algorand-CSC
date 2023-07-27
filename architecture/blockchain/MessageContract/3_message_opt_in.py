from algosdk.atomic_transaction_composer import *
from pyteal import *
from decouple import config

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

DATAOWNER_ADDRESS = config('DATAOWNER_ADDRESS')
DATAOWNER_PRIVATEKEY = config('DATAOWNER_PRIVATEKEY')
APP_ID = config('APPLICATION_ID_MESSAGES')


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address = DATAOWNER_ADDRESS
    private_key = DATAOWNER_PRIVATEKEY
    app_id = APP_ID

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
