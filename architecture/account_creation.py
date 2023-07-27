from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "p8IwM35NPv3nRf0LLEquJ5tmpOtcC4he7KKnJ3wE"
headers = {
   "X-API-Key": algod_token,
}

algod_client = algod.AlgodClient(algod_token, algod_address, headers)


def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

generate_algorand_keypair()

#My address: LK7F5TUSXIEKLHN7SXJ6STLHVZEPT5AJKE5LEBM6FVZMZGCCHXYSII35C4
#My private key: mgvW3xKXsHwmCuLpmy1s5Pok6xzmjgLL+QbSg/pWwF1avl7OkroIpZ2/ldPpTWeuSPn0CVE6sgWeLXLMmEI98Q==
#My passphrase: infant flag husband illness gentle palace eye tilt large reopen current purity enemy depart couch moment gate transfer address diamond vital between unlock able cave
