from algosdk.atomic_transaction_composer import *
from pyteal import *

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

AUTHORITY1_ADDRESS="NBKP3E7M4OVO3SV3FEJQQ2Z2NVMRQMRWS654MMLCKSKXGLRFMF5Z6ACGCA"
AUTHORITY1_PRIVATEKEY="UPabOwAKUe6wNsm7VmAgTeZ3kYEmd7cep2SDv03vIppoVP2T7OOq7cq7KRMIazptWRgyNpe7xjFiVJVzLiVhew=="

AUTHORITY2_ADDRESS="XE36THD3UXASJ4DMF4W3WZV4KCZQZYJR2LJCUHJDHTTLLTUXY22JZ4QK3U"
AUTHORITY2_PRIVATEKEY="5xYZ1QiDTTTcpqluwgbbssUT+2seRAdeP9ffBUnVaQG5N+mce6XBJPBsLy27ZrxQswzhMdLSKh0jPOa1zpfGtA=="

AUTHORITY3_ADDRESS="54MW2OHJNUOT3ZERNYDWAOLL5ZB2WDQVB42DFAIXVZI53HYF3LBOWZTSYY"
AUTHORITY3_PRIVATEKEY="jp7yX4KFLtCeYeiE7um1B3NnWqh5colD0JgZJOOcPq7vGW046W0dPeSRbgdgOWvuQ6sOFQ80MoEXrlHdnwXawg=="

AUTHORITY4_ADDRESS="Z5ZNF7XYPNUPCQGUAUUI3F5UCWPV7KNORRRMR4KPUSFGVQSQO3QYNXQSXA"
AUTHORITY4_PRIVATEKEY="KGp9AMLxmDw9WFovIYkawDB9Yzlel1aqtC/PmOkCRBzPctL++Hto8UDUBSiNl7QVn1+proxiyPFPpIpqwlB24Q=="

def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    address=AUTHORITY1_ADDRESS
    private_key=AUTHORITY1_PRIVATEKEY
    app_id=239796376

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