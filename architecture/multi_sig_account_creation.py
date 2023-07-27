###ACCOUNT 1
# My address: VOXXQITDR5QMSS3K7XZHTGED5H2S6HEUS7QMWZBBQJYGJSNUN6XIPZAAPQ
# My private key: VZtHXj4T2DT2atlThLRuOgPE0n+bj9sO6e/6STgm3Nqrr3giY49gyUtq/fJ5mIPp9S8clJfgy2QhgnBkybRvrg==
# My passphrase: height bunker connect crop rabbit minor fish sunny media spirit dance crisp marine visa swim moon swarm picnic jewel panic identify another street absorb ladder

###ACCOUNT 2
# My address: RCYGIB2BFYZTTHVF7KPV5TXVAMY5Y4M2NONPKMQPLXSV65FY4HBFFH2GVY
# My private key: v1NEi7llgXaH66aofgHv+/8RW3MsOUmqneWc/Tm97n+IsGQHQS4zOZ6l+p9ezvUDMdxxmmua9TIPXeVfdLjhwg==
# My passphrase: jewel bacon shield fortune actress tank found plunge steak album wasp zero catalog strategy glory decrease empty issue index supply initial quantum youth about duty

###ACCOUNT 3
# My address: XUIUSKTUOXXLECGGU2YLJO3AW4BXDYAF4P2QFCKBXMONJHS4DCNXT5CQJA
# My private key: nOewRj9MCGANg7oSlpqc6YO+2zl+2SBzp70/W4MlEka9EUkqdHXusgjGprC0u2C3A3HgBeP1AolBuxzUnlwYmw==
# My passphrase: vicious seminar person sentence awesome fix blur ritual seat heart soft direct laptop ivory vault sunny goat oven tell recycle allow maximum correct able kiwi

from algosdk import mnemonic, account
from algosdk.transaction import Multisig
# Shown for demonstration purposes. NEVER reveal secret mnemonics in practice.
# Change these values to use the accounts created previously.
# Change these values with mnemonics
mnemonic1 = "height bunker connect crop rabbit minor fish sunny media spirit dance crisp marine visa swim moon swarm picnic jewel panic identify another street absorb ladder"
mnemonic2 = "jewel bacon shield fortune actress tank found plunge steak album wasp zero catalog strategy glory decrease empty issue index supply initial quantum youth about duty"
mnemonic3 = "vicious seminar person sentence awesome fix blur ritual seat heart soft direct laptop ivory vault sunny goat oven tell recycle allow maximum correct able kiwi"

private_key_1 = mnemonic.to_private_key(mnemonic1)
account_1 = account.address_from_private_key(private_key_1)

private_key_2 = mnemonic.to_private_key(mnemonic2)
account_2 = account.address_from_private_key(private_key_2)

private_key_3 = mnemonic.to_private_key(mnemonic3)
account_3 = account.address_from_private_key(private_key_3)

# create a multisig account
version = 1  # multisig version
threshold = 2  # how many signatures are necessary
msig = Multisig(version, threshold, [account_1, account_2, account_3])
print("Multisig Address: ", msig.address())
# print('Go to the below link to fund the created account using testnet faucet: \n https://dispenser.testnet.aws.algodev.network/?account={}'.format(msig.address())) 


# Multisig Address:  KBXZ3WR2WPKKZQUXNIXVLYC7AIWQCLEA2O2UPAETWLPFSSYD5XGY2YGU6U







