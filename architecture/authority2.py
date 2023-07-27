from charm.toolbox.pairinggroup import *
from decouple import config
import mpc_setup
from maabe_class import *
import ipfshttpclient
from charm.core.engine.util import objectToBytes, bytesToObject
import os
import sys
import io
import base64
import subprocess
from algosdk.encoding import decode_address, encode_address
import ast
import sqlite3

app_id_box = config('APPLICATION_ID_BOX')

authority2_mnemonic = config('AUTHORITY2_MNEMONIC')
authority2_private_key = config('AUTHORITY2_PRIVATEKEY')
authority2_address = config('AUTHORITY2_ADDRESS')
authority1_address = config('AUTHORITY1_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']

# Connection to SQLite3 authority2 database
conn = sqlite3.connect('files/authority2/authority2.db')
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

    authorities_name = hash_file + '#'
    padding = '0' * 405
    authorities_name_padded = authorities_name + padding

    x.execute("INSERT OR IGNORE INTO authority_names VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority2_private_key, method, app_id_box, authorities_name_padded)))


def initial_parameters_hashed(groupObj, process_instance_id):
    g1_2 = groupObj.random(G1)
    g2_2 = groupObj.random(G2)
    (h1_2, h2_2) = mpc_setup.commit(groupObj, g1_2, g2_2)

    x.execute("INSERT OR IGNORE INTO h_values VALUES (?,?,?)", (process_instance_id, h1_2, h2_2))
    conn.commit()

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority2_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')
    authorities = result[:47]
    hashed = authorities + h1_2 + ',' + h2_2 + '#'
    padding = '0' * 275
    hashed_padded = hashed + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority2_private_key, method, app_id_box, hashed_padded)))

    g1_2_bytes = groupObj.serialize(g1_2)
    g2_2_bytes = groupObj.serialize(g2_2)

    x.execute("INSERT OR IGNORE INTO g_values VALUES (?,?,?)", (process_instance_id, g1_2_bytes, g2_2_bytes))
    conn.commit()


def initial_parameters(process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_2_bytes = result[0][1]
    g2_2_bytes = result[0][2]

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority2_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')

    elements = g1_2_bytes.decode('utf-8') + ',' + g2_2_bytes.decode('utf-8') + '#'
    hashed_elements = result[:177] + elements
    padding = '0' * 93
    hashed_elements_padded = hashed_elements + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority2_private_key, method, app_id_box, hashed_elements_padded)))


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    g1_2_bytes = result[0][1]
    g1_2 = groupObj.deserialize(g1_2_bytes)
    g2_2_bytes = result[0][2]
    g2_2 = groupObj.deserialize(g2_2_bytes)

    x.execute("SELECT * FROM h_values WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    h1 = result[0][1]
    h2 = result[0][2]

    method = 'read_specific_box'
    ####################
    #######AUTH1########
    ####################
    box_name = base64.b64encode(decode_address(authority1_address))
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', method,
                             app_id_box, box_name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    result = ast.literal_eval(result)
    all_elements = base64.b64decode(result['value']).decode('utf-8')
    all_elements = all_elements.split('#')
    g1g2_1_hashed = all_elements[1]
    g1g2_1_hashed_split = g1g2_1_hashed.split(',')

    g1g2_1 = all_elements[2]
    g1g2_1_split = g1g2_1.split(',')

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
    ##########VALUES#############
    #############################

    g1_1 = g1g2_1_split[0]
    g1_1 = bytes(g1_1, 'utf-8')
    g1_1 = groupObj.deserialize(g1_1)
    g2_1 = g1g2_1_split[1]
    g2_1 = bytes(g2_1, 'utf-8')
    g2_1 = groupObj.deserialize(g2_1)

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

    hashes1 = [g1g2_1_hashed_split[0], h1, g1g2_3_hashed_split[0], g1g2_4_hashed_split[0]]
    hashes2 = [g1g2_1_hashed_split[1], h2, g1g2_3_hashed_split[1], g1g2_4_hashed_split[1]]
    com1 = [g1_1, g1_2, g1_3, g1_4]
    com2 = [g2_1, g2_2, g2_3, g2_4]
    (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)

    public_parameters = maabe.setup(value1, value2)
    public_parameters_reduced = dict(list(public_parameters.items())[0:3])
    pp_reduced = objectToBytes(public_parameters_reduced, groupObj)

    file_to_str = pp_reduced.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)", (process_instance_id, hash_file, file_to_str))
    conn.commit()

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority2_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')

    hashed_elements_pp = result[:359] + hash_file + '#'
    padding = '0' * 46
    hashed_elements_pp_padded = hashed_elements_pp + padding

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority2_private_key, method, app_id_box, hashed_elements_pp_padded)))


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (process_instance_id,))
    result = x.fetchall()
    public_parameters = result[0][2].encode()
    return public_parameters


def generate_pk_sk(groupObj, maabe, api, process_instance_id):
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F

    # authsetup 2AA
    (pk2, sk2) = maabe.authsetup(public_parameters, 'OU')
    pk2_bytes = objectToBytes(pk2, groupObj)
    sk2_bytes = objectToBytes(sk2, groupObj)

    file_to_str = pk2_bytes.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')

    x.execute("INSERT OR IGNORE INTO private_keys VALUES (?,?)", (process_instance_id, sk2_bytes))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO public_keys VALUES (?,?,?)", (process_instance_id, hash_file, pk2_bytes))
    conn.commit()

    method = 'read_box'
    result = subprocess.run(['python3.10', 'blockchain/BoxContract/BoxContractMain.py', authority2_private_key, method,
                             app_id_box], stdout=subprocess.PIPE).stdout.decode('utf-8')
    hashed_elements_pp_pk = result[:406] + hash_file

    method = 'put_box'
    print(os.system('python3.10 blockchain/BoxContract/BoxContractMain.py %s %s %s %s' % (
        authority2_private_key, method, app_id_box, hashed_elements_pp_pk)))


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


if __name__ == '__main__':
    main()
