from AttributeCertifierContract import *
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
import sys
from algosdk import account, transaction
from decouple import config
from algosdk.v2client import algod
import base64

# user declared account mnemonics
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


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def createApp(
        algod_client: algod.AlgodClient
) -> int:
    local_ints = 0
    local_bytes = 0
    global_ints = 2
    global_bytes = 2
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # Compile the program
    router = getRouter()
    approval_program, clear_program, contract = router.compile_program(version=6)

    with open("attr_approval.teal", "w") as f:
        f.write(approval_program)

    with open("attr_clear.teal", "w") as f:
        f.write(clear_program)

    with open("attr_contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))

    approval_program_compiled = compile_program(algod_client, approval_program)

    clear_state_program_compiled = compile_program(algod_client, clear_program)

    print("--------------------------------------------")
    print("Deploying application......")

    # define sender as creator
    sender = msig.address()

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = algod_client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
    )

    mtx = transaction.MultisigTransaction(txn, msig)
    mtx.sign(pk_attribute_certifier_1)
    mtx.sign(pk_attribute_certifier_2)

    # sign transaction
    # signed_txn = txn.sign(private_key)
    tx_id = mtx.transaction.get_txid()

    # send transaction
    algod_client.send_transactions([mtx])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 5)
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
    transaction_response = algod_client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id


def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "voted":
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = (
        app["params"]["global-state"] if "global-state" in app["params"] else []
    )
    return format_state(global_state)


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    app_id = createApp(algod_client)
    print("Global state:", read_global_state(algod_client, app_id))


if __name__ == "__main__":
    main()
