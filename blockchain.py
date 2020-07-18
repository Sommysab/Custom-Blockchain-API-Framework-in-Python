import datetime, hashlib, json, requests
from uuid import uuid4


class Blockchain:

    def __init__(self): 
        self.chain = []
        # block transactions
        self.transactions = [] 
        # Genesis Block
        self.create_block(proof=1, previous_hash='0')
        # Placeholder Url for the node (or 127.0.0.1:5003)
        node_url =  str(uuid4()).replace('-', '')
        # dictionary for all nodes in the network
        self.nodes = set() 
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = [] # re-initialize block transactions        
        self.chain.append(block) # Add new block to the block chain
        return block

    def get_previous_block(self):
        return self.chain[-1]

    # Basic Proof of Work Algorithim
    def proof_of_work(self, previous_proof):
        # initialization
        new_proof = 1
        check_proof = False
        # logic
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]== '0000':
                check_proof = True 
            else:
                new_proof +=1 
            
        return new_proof

    # Block hashing method
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode() # converting to bytes
        return hashlib.sha256(encoded_block).hexdigest()

    # Block validation method 
    def is_chain_valid(self, chain):
        # initializing 
        previous_block = chain[0]
        block_index = 1 
        # logic 
        while block_index < len(chain):
            block = chain[block_index] 
            if block['previous_hash'] != self.hash(previous_block):
                return False # 

            # Check prev proof and current proof starts with 4 leading zeros
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            # update current block for the loop
            previous_block = block
            block_index += 1
        
        return True

    # Transactions added for current newly minned block
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append(
            {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }
        )
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    # New Nodes in the blockchain
    def add_node(self, url):
        parsed_url =  urlparse(url)
        self.nodes.add(parsed_url.netloc)

    # Concensus
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)  # current Node chain length
        
        for node in network:
            res = requests.get(f'http://{node}/get_chain')
            if res.status_code == 200:
                length = res.json()['length'] #lenght key in the chain object returned
                chain = res.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    break
            
        if longest_chain:
            self.chain = longest_chain
            return True
            
        return False

