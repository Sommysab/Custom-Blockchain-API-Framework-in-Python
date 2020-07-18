import json
from flask import Flask, jsonify, request
app = Flask(__name__) 


import blockchain
blockchain = Blockchain() 


# Mining block route
@app.route('/mine_block', methods=['GET']) 
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof) 
    previous_hash = blockchain.hash(previous_block)
    # Transactions from newly mined block
    blockchain.add_transaction(sender= blockchain.node_url, receiver='Sab', amount=1) 
    # Create Block for work done
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Block mined!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }

    return jsonify(response), 200 

# Get the full chain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


# Validate blockchain
@app.route('/is_valid', methods=['GET'])
def is_valid():  
    validation = blockchain.is_chain_valid(blockchain.chain) 
    if validation==True:
        return jsonify({'message': 'validation true'}), 200
    else:
        return jsonify({'message': 'validation false'}), 200


# Add transaction to the blockchain 
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be add to block {index}'}
    return jsonify(response), 201


# Connect new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400

    for node in nodes: 
        blockchain.add_node(node)

    response = {
        'message': 'All the nodes are now connected. The Agcoin Blockchain now has:',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


# Update the chain with Longest Chain
@app.route('/replace_chain', methods=['GET'])
def replace_chain():  
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced==True:
        response = {
            'message': 'BlockChain Updated',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'BlockChain not changed',
            'actual_chain': blockchain.chain
        }

    return jsonify(response), 200

app.run(host='0.0.0.0', port = 5003)