from contract import *
from algosdk.atomic_transaction_composer import *
from algosdk import account
from pyteal import *

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
    "X-API-Key": algod_token,
}

DATAOWNER_ADDRESS='SVCAKVYOAWOUKTB4YK3DQH2SCEMAKZ3OVLXIBUANDMJNOI7COXUO34NWG4'
DATAOWNER_PRIVATEKEY='8iTtNZ9wCphZUYjQrE8r3SHcSDb7r6xBr0Gn9Avm4UCVRAVXDgWdRUw8wrY4H1IRGAVnbqrugNANGxLXI+J16A=='

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

    with open("./msg_contract.json") as f:
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


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    print("Saving message in the application......")
    app_id = 211214277
    sender_private_key=DATAOWNER_PRIVATEKEY
    message_id = 123456
    hash_file = 'QwTEST'
    saveData(algod_client, sender_private_key, app_id, message_id, hash_file)



if __name__ == "__main__":
    main()