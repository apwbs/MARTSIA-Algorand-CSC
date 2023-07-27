import base64
from algosdk import abi, atomic_transaction_composer, logic
from algosdk import transaction
from algosdk.v2client import algod
from algosdk import account
from algosdk import mnemonic
from algosdk.encoding import decode_address, encode_address
import sys
from algosdk.v2client import indexer
from decouple import config


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

# creator_mnemonic = "infant flag husband illness gentle palace eye tilt large reopen current purity enemy depart couch moment gate transfer address diamond vital between unlock able cave"
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}


def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


def compile_program(client: algod.AlgodClient, source_code: bytes) -> bytes:
    compile_response = client.compile(source_code.decode("utf-8"))
    return base64.b64decode(compile_response["result"])


# Creates an app and returns the app ID
def create_test_app() -> int:
    client = algod.AlgodClient(algod_token, algod_address, headers)

    # Declare application state storage (immutable)
    local_ints = 1
    local_bytes = 1
    global_ints = 1
    global_bytes = 1

    # Define app schema
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)
    on_complete = transaction.OnComplete.NoOpOC.real

    # Compile the program with algod
    with open("approve-box.teal", mode="rb") as file:
        source_code = file.read()
    with open("clear-box.teal", mode="rb") as file:
        clear_code = file.read()
    source_program = compile_program(client, source_code)
    clear_program = compile_program(client, clear_code)

    sender = msig.address()
    on_complete = transaction.OnComplete.NoOpOC.real
    params = client.suggested_params()

    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        source_program,
        clear_program,
        global_schema,
        local_schema,
    )

    mtx = transaction.MultisigTransaction(txn, msig)
    mtx.sign(pk_attribute_certifier_1)
    mtx.sign(pk_attribute_certifier_2)
    tx_id = mtx.transaction.get_txid()

    # send transaction
    client.send_transactions([mtx])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 5)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                transaction_response["confirmed-round"]
            )
        )

    except Exception as err:
        print(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id


def fund_program(app_id: int):
    client = algod.AlgodClient(algod_token, algod_address, headers)
    sender = msig.address()

    # Send transaction to fund the app.
    txn = transaction.PaymentTxn(
        sender,
        client.suggested_params(),
        logic.get_application_address(app_id),
        5_000_000,
    )

    mtx = transaction.MultisigTransaction(txn, msig)
    mtx.sign(pk_attribute_certifier_1)
    mtx.sign(pk_attribute_certifier_2)
    tx_id = mtx.transaction.get_txid()

    # send transaction
    client.send_transactions([mtx])
    _ = transaction.wait_for_confirmation(client, tx_id, 5)


if __name__ == "__main__":
    #############
    ###1st run###
    #############
    # app_id = create_test_app()

    #############
    ###2nd run###
    #############
    app_id = 264486342
    fund_program(app_id)
