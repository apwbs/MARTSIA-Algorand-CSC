from MessageContract import *
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
from algosdk.abi import Method, Contract
import sys
import base64
from algosdk import account

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

def get_method(name: str, js: str) -> Method:
    c = Contract.from_json(js)
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with the name {}".format(name))

def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            formatted_value = base64.b64decode(value["bytes"])
            if formatted_key == 'authorityAddress':
                formatted[formatted_key] = encode_address(formatted_value)
            else:
                formatted[formatted_key] = formatted_value
        else:
            formatted[formatted_key] = value["uint"]
    return formatted


def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = (
        app["params"]["global-state"] if "global-state" in app["params"] else []
    )
    return format_state(global_state)


def saveData(
        client: algod.AlgodClient,
        sender: str,
        app_id: int,
        message_id: str,
        hash_file: str,
) -> None:
    atc = AtomicTransactionComposer()
    signer = AccountTransactionSigner(sender)
    sp = client.suggested_params()

    app_args = [
        message_id,
        hash_file
    ]

    with open("blockchain/Controlled/multisig/MessageContract/contract.json") as f:
        js = f.read()
    atc.add_method_call(
        app_id=app_id,
        method=get_method('on_save', js),
        sender=account.address_from_private_key(sender),
        sp=sp,
        signer=signer,
        method_args=app_args
    )

    result = atc.execute(client, 10)

    print("Transaction id:", result.tx_ids[0])

    print("Global state:", read_global_state(client, app_id))


def main(params):
    sender_private_key = params[1]

    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    print("--------------------------------------------")
    print("Saving message in the application......")
    print('Im using this one')
    app_id = params[2]
    message_id = params[3]
    hash_file = params[4]
    saveData(algod_client, sender_private_key, app_id, message_id, hash_file)


if __name__ == "__main__":
    main(sys.argv)
