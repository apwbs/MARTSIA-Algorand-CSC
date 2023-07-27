from algosdk.atomic_transaction_composer import *
from pyteal import *
from decouple import config

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

AUTHORITY1_ADDRESS = config('AUTHORITY1_ADDRESS')
AUTHORITY1_PRIVATEKEY = config('AUTHORITY1_PRIVATEKEY')
AUTHORITY2_ADDRESS = config('AUTHORITY2_ADDRESS')
AUTHORITY2_PRIVATEKEY = config('AUTHORITY2_PRIVATEKEY')
AUTHORITY3_ADDRESS = config('AUTHORITY3_ADDRESS')
AUTHORITY3_PRIVATEKEY = config('AUTHORITY3_PRIVATEKEY')
AUTHORITY4_ADDRESS = config('AUTHORITY4_ADDRESS')
AUTHORITY4_PRIVATEKEY = config('AUTHORITY4_PRIVATEKEY')
APP_ID = config('APPLICATION_ID_BOX')


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address = AUTHORITY1_ADDRESS
    private_key = AUTHORITY1_PRIVATEKEY
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
