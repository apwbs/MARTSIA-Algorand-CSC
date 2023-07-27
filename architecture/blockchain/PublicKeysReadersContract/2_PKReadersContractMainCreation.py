import PKReadersContract
from algosdk import account, transaction
from algosdk.v2client import algod
import base64

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

def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def createApp(client: algod.AlgodClient) -> int:
    local_ints = 1
    local_bytes = 0
    global_ints = 1
    global_bytes = 3
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # Compile the program
    router = PKReadersContract.getRouter()
    approval_program, clear_program, contract = router.compile_program(version=6)

    with open("pk_readers_approval.teal", "w") as f:
        f.write(approval_program)

    with open("pk_readers_clear.teal", "w") as f:
        f.write(clear_program)

    with open("pk_readers_contract.json", "w") as f:
        import json

        f.write(json.dumps(contract.dictify()))

    approval_program_compiled = compile_program(client, approval_program)

    clear_state_program_compiled = compile_program(client, clear_program)

    # define sender as creator
    sender = msig.address()

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

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
    mtx.sign(private_key_1)
    mtx.sign(private_key_2)

    # sign transaction
    # signed_txn = txn.sign(private_key)
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
    