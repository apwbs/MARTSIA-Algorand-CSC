from algosdk.atomic_transaction_composer import *
from pyteal import *

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

READER_ADDRESS_MANUFACTURER="RVBQ5PURO5LXR6N7Y4SGQOUGFLXH37KB56OOTXMPJUIMYSOVPTJNYTS45Y"
READER_PRIVATEKEY_MANUFACTURER="ii6dnN0HIMfZW2MOqKR9LsB9VS1Et9UrNE9E+RnlHPaNQw6+kXdXePm/xyRoOoYq7n39Qe+c6d2PTRDMSdV80g=="

READER_ADDRESS_SUPPLIER1="GVYFQRX3MVD5ZKFK4QDW34X2B7E2BEOQO6JF7CM3HMRR4XTZTX2DST6CQU"
READER_PRIVATEKEY_SUPPLIER1="CPFzPu5oqIsOwbfSy0KGGCJNVfXkSKmJjNpL0JJgR/Q1cFhG+2VH3Kiq5Adt8voPyaCR0HeSX4mbOyMeXnmd9A=="

READER_ADDRESS_SUPPLIER2="T7ZIDGUWMELKADPMAYW6BETSL5PT6UQOYRZC6PE24RNUYAKLNFHJFMBMJI"
READER_PRIVATEKEY_SUPPLIER2="b9L4YCdfVEm/tzFPH2XgoVD+a1NjwIZR+2cUR7woDjif8oGalmEWoA3sBi3gknJfXz9SDsRyLzya5FtMAUtpTg=="


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address=READER_ADDRESS_SUPPLIER2
    private_key=READER_PRIVATEKEY_SUPPLIER2
    app_id=248937298

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