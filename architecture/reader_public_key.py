from decouple import config
import os
from Crypto.PublicKey import RSA
from hashlib import sha512
import ipfshttpclient
import sqlite3
import io

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
app_id_pk_readers = config('APPLICATION_ID_PK_READERS')

manufacturer_address = config('READER_ADDRESS_MANUFACTURER')
manufacturer_private_key = config('READER_PRIVATEKEY_MANUFACTURER')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
electronics_private_key = config('READER_PRIVATEKEY_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')
mechanics_private_key = config('READER_PRIVATEKEY_SUPPLIER2')

reader_address = mechanics_address
private_key = mechanics_private_key

# Connection to SQLite3 reader database
conn = sqlite3.connect('files/reader/reader.db')
x = conn.cursor()


def generate_keys():
    keyPair = RSA.generate(bits=1024)
    # print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    # print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")

    f = io.StringIO()
    f.write('reader_address: ' + reader_address + '###')
    f.write(str(keyPair.n) + '###' + str(keyPair.e))
    f.seek(0)

    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')

    # reader address not necessary because each user has one key. Since we use only one 'reader/client' for all the
    # readers, we need a distinction.
    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)", (reader_address, str(keyPair.n), str(keyPair.d)))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
              (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
    conn.commit()

    # name_file1 = 'files/keys_readers/handshake_private_key_' + str(reader_address) + '.txt'
    # with open(name_file1, 'w') as ipfs:
    #     ipfs.write('reader_address: ' + reader_address + '###')
    #     ipfs.write(str(keyPair.n) + '###' + str(keyPair.d))

    # name_file = 'files/keys_readers/handshake_public_key_' + str(reader_address) + '.txt'
    # with open(name_file, 'w') as ipfs:
    #     ipfs.write('reader_address: ' + reader_address + '###')
    #     ipfs.write(str(keyPair.n) + '###' + str(keyPair.e))
    # new_file = api.add(name_file)
    # hash_file = new_file['Hash']
    # print(f'ipfs hash: {hash_file}')

    print(os.system('python3.10 blockchain/PublicKeysReadersContract/PKReadersContractMain.py %s %s %s' % (
        private_key, app_id_pk_readers, hash_file)))


if __name__ == "__main__":
    generate_keys()
