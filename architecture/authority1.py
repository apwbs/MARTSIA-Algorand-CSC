import json

from charm.toolbox.pairinggroup import *
from maabe_class import *
import mpc_setup
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import os
import sys
import io
import base64
import sqlite3
import subprocess
from algosdk.encoding import decode_address, encode_address
import ast

app_id_box = config('APPLICATION_ID_BOX')

authority1_mnemonic = config('AUTHORITY1_MNEMONIC')
authority1_private_key = config('AUTHORITY1_PRIVATEKEY')
authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']

# Connection to SQLite3 authority1 database
conn = sqlite3.connect('files/authority1/authority1.db')
x = conn.cursor()


def save_authorities_names(api, process_instance_id):
    f = io.StringIO()
    for i, addr in enumerate(authorities_list):
        f.write('process_instance: ' + str(process_instance_id) + '\n')
        f.write('identification: ' + 'authority ' + str(i + 1) + '\n')
        f.write('name: ' + str(authorities_names[i]) + '\n')
        f.write('address: ' + addr + '\n\n')
    f.seek(0)

    file_to_str = f.read()

    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    # a = api.get_json('QmXzPjFFgK5RB6iX4jRe3jWNRX8kz2imjJpUQdQyvcymqj')
    # print(a)

    # name_file = 'files/authority1/authorities_names_au1_' + str(process_instance_id) + '.txt'
    # with open(name_file, 'w') as ua:
    #     for i, addr in enumerate(authorities_list):
    #         ua.write('identification: ' + 'authority ' + str(i + 1) + '\n')
    #         ua.write('name: ' + 'UT' + '\n')
    #         ua.write('address: ' + addr + '\n\n')
    #
    # new_file = api.add(name_file)
    # hash_file = new_file['Hash']
    # print(f'ipfs hash: {hash_file}')

    authorities_name = hash_file + '#'
    padding = '0' * 405
    authorities_name_padded = authorities_name + padding

    x.execute("INSERT OR IGNORE INTO authority_names VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    # x.execute("SELECT * FROM authority_names WHERE process_instance=?", (process_instance_id,))
    # result = x.fetchall()
    # with open('files/authority1/test.txt', 'w') as u1:
    #     u1.write(result[0][1])

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority1_private_key, method, app_id_box, authorities_name_padded)))


def initial_parameters_hashed(groupObj, process_instance_id):
    g1_1 = groupObj.random(G1)
    g2_1 = groupObj.random(G2)
    (h1_1, h2_1) = mpc_setup.commit(groupObj, g1_1, g2_1)

    x.execute("INSERT OR IGNORE INTO h_values VALUES (?,?,?)", (process_instance_id, h1_1, h2_1))
    conn.commit()

    # with open('files/authority1/h1_1_' + str(process_instance_id) + '.txt', 'w') as h1_1w:
    #     h1_1w.write(h1_1)
    #
    # with open('files/authority1/h2_1_' + str(process_instance_id) + '.txt', 'w') as h2_1w:
    #     h2_1w.write(h2_1)

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority1_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')
    authorities = result[:47]
    hashed = authorities + h1_1 + ',' + h2_1 + '#'
    padding = '0' * 275
    hashed_padded = hashed + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority1_private_key, method, app_id_box, hashed_padded)))

    g1_1_bytes = groupObj.serialize(g1_1)
    g2_1_bytes = groupObj.serialize(g2_1)

    x.execute("INSERT OR IGNORE INTO g_values VALUES (?,?,?)", (process_instance_id, g1_1_bytes, g2_1_bytes))
    conn.commit()

    # with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'wb') as g1_1w:
    #     g1_1w.write(g1_1_bytes)
    #
    # with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'wb') as g2_1w:
    #     g2_1w.write(g2_1_bytes)


def initial_parameters(process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_1_bytes = result[0][1]
    g2_1_bytes = result[0][2]

    # with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'rb') as g1:
    #     g1_1_bytes = g1.read()

    # with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'rb') as g2:
    #     g2_1_bytes = g2.read()

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority1_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')
    elements = g1_1_bytes.decode('utf-8') + ',' + g2_1_bytes.decode('utf-8') + '#'
    hashed_elements = result[:177] + elements
    padding = '0' * 93
    hashed_elements_padded = hashed_elements + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority1_private_key, method, app_id_box, hashed_elements_padded)))


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_1_bytes = result[0][1]
    g1_1 = groupObj.deserialize(g1_1_bytes)
    g2_1_bytes = result[0][2]
    g2_1 = groupObj.deserialize(g2_1_bytes)

    # with open('files/authority1/g1_1_' + str(process_instance_id) + '.txt', 'rb') as g1:
    #     g1_1_bytes = g1.read()
    # g1_1 = groupObj.deserialize(g1_1_bytes)

    # with open('files/authority1/g2_1_' + str(process_instance_id) + '.txt', 'rb') as g2:
    #     g2_1_bytes = g2.read()
    # g2_1 = groupObj.deserialize(g2_1_bytes)

    x.execute("SELECT * FROM h_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    h1 = result[0][1]
    h2 = result[0][2]

    # with open('files/authority1/h1_1_' + str(process_instance_id) + '.txt', 'r') as h1:
    #     h1 = h1.read()

    # with open('files/authority1/h2_1_' + str(process_instance_id) + '.txt', 'r') as h2:
    #     h2 = h2.read()

    method = 'read_specific_box'
    ####################
    #######AUTH2########
    ####################
    box_name = base64.b64encode(decode_address(authority2_address))
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', method,
                             app_id_box, box_name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    result = ast.literal_eval(result)
    all_elements = base64.b64decode(result['value']).decode('utf-8')
    all_elements = all_elements.split('#')
    g1g2_2_hashed = all_elements[1]
    g1g2_2_hashed_split = g1g2_2_hashed.split(',')

    g1g2_2 = all_elements[2]
    g1g2_2_split = g1g2_2.split(',')

    ####################
    #######AUTH3########
    ####################
    box_name = base64.b64encode(decode_address(authority3_address))
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', method,
                             app_id_box, box_name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    result = ast.literal_eval(result)
    all_elements = base64.b64decode(result['value']).decode('utf-8')
    all_elements = all_elements.split('#')
    g1g2_3_hashed = all_elements[1]
    g1g2_3_hashed_split = g1g2_3_hashed.split(',')

    g1g2_3 = all_elements[2]
    g1g2_3_split = g1g2_3.split(',')

    ####################
    #######AUTH4########
    ####################
    box_name = base64.b64encode(decode_address(authority4_address))
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', method,
                             app_id_box, box_name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    result = ast.literal_eval(result)
    all_elements = base64.b64decode(result['value']).decode('utf-8')
    all_elements = all_elements.split('#')
    g1g2_4_hashed = all_elements[1]
    g1g2_4_hashed_split = g1g2_4_hashed.split(',')

    g1g2_4 = all_elements[2]
    g1g2_4_split = g1g2_4.split(',')

    #############################
    ##########ELEMENTS###########
    #############################

    g1_2 = g1g2_2_split[0]
    g1_2 = bytes(g1_2, 'utf-8')
    g1_2 = groupObj.deserialize(g1_2)
    g2_2 = g1g2_2_split[1]
    g2_2 = bytes(g2_2, 'utf-8')
    g2_2 = groupObj.deserialize(g2_2)

    g1_3 = g1g2_3_split[0]
    g1_3 = bytes(g1_3, 'utf-8')
    g1_3 = groupObj.deserialize(g1_3)
    g2_3 = g1g2_3_split[1]
    g2_3 = bytes(g2_3, 'utf-8')
    g2_3 = groupObj.deserialize(g2_3)

    g1_4 = g1g2_4_split[0]
    g1_4 = bytes(g1_4, 'utf-8')
    g1_4 = groupObj.deserialize(g1_4)
    g2_4 = g1g2_4_split[1]
    g2_4 = bytes(g2_4, 'utf-8')
    g2_4 = groupObj.deserialize(g2_4)

    #############################
    ##########VALUES#############
    #############################

    hashes1 = [h1, g1g2_2_hashed_split[0], g1g2_3_hashed_split[0], g1g2_4_hashed_split[0]]
    hashes2 = [h2, g1g2_2_hashed_split[1], g1g2_3_hashed_split[1], g1g2_4_hashed_split[1]]
    com1 = [g1_1, g1_2, g1_3, g1_4]
    com2 = [g2_1, g2_2, g2_3, g2_4]
    (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)

    # setup
    public_parameters = maabe.setup(value1, value2)
    public_parameters_reduced = dict(list(public_parameters.items())[0:3])
    pp_reduced = objectToBytes(public_parameters_reduced, groupObj)

    file_to_str = pp_reduced.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    # name_file = 'files/authority1/public_parameters_authority1_' + str(process_instance_id) + '.txt'
    # with open(name_file, 'wb') as ipfs:
    #     ipfs.write(pp_reduced)
    # new_file = api.add(name_file)
    # hash_file = new_file['Hash']
    # print(f'ipfs hash: {hash_file}')

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority1_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')

    hashed_elements_pp = result[:359] + hash_file + '#'
    padding = '0' * 46
    hashed_elements_pp_padded = hashed_elements_pp + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority1_private_key, method, app_id_box, hashed_elements_pp_padded)))


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    public_parameters = result[0][2].encode()

    # with open('files/authority1/public_parameters_authority1_' + str(process_instance_id) + '.txt', 'rb') as ppa2:
    #     public_parameters = ppa2.read()

    return public_parameters


def generate_pk_sk(groupObj, maabe, api, process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # authsetup 2AA
    (pk1, sk1) = maabe.authsetup(public_parameters, 'UT')
    pk1_bytes = objectToBytes(pk1, groupObj)
    sk1_bytes = objectToBytes(sk1, groupObj)

    file_to_str = pk1_bytes.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO private_keys VALUES (?,?)", (process_instance_id, sk1_bytes))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO public_keys VALUES (?,?,?)", (process_instance_id, hash_file, pk1_bytes))
    conn.commit()

    # name_file = 'files/authority1/authority_ut_pk_' + str(process_instance_id) + '.txt'
    # with open(name_file, 'wb') as a1:
    #     a1.write(pk1_bytes)
    # with open('files/authority1/private_key_au1_' + str(process_instance_id) + '.txt', 'wb') as as1:
    #     as1.write(sk1_bytes)
    # new_file = api.add(name_file)
    # hash_file = new_file['Hash']
    # print(f'ipfs hash: {hash_file}')

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority1_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')
    hashed_elements_pp_pk = result[:406] + hash_file

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority1_private_key, method, app_id_box, hashed_elements_pp_pk)))


def main():
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(app_id_box)

    ###########
    ###########
    ###LINES###
    ###########
    ###########
    # save_authorities_names(api, process_instance_id)
    # initial_parameters_hashed(groupObj, process_instance_id)
    # initial_parameters(process_instance_id)
    # generate_public_parameters(groupObj, maabe, api, process_instance_id)
    generate_pk_sk(groupObj, maabe, api, process_instance_id)

    # test = api.name.publish('/ipfs/' + hash_file)
    # print(test)
    # os.system('ipfs cat ' + hash_file)
    # os.system('ipfs name publish /ipfs/' + hash_file)


if __name__ == '__main__':
    main()
