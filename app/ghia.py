from flask import Flask
from flask import request
import json
import hmac
import hashlib

app = Flask(__name__)

hooks = []
w_secret = 'WjMTejwojlt7wfZw3PB3'


def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


@app.route('/', methods=['POST'])
def gitHub(captain_hook):
    x_hub_signature = request.headers.get('X - Hub - Signature')

    if is_valid_signature(x_hub_signature, request.data, w_secret):
        hooks.append(captain_hook)


@app.route('/hooks')
def index():
    return "Hello World!\n" + json.dumps(hooks)


if __name__ == '__main__':
    app.run()
