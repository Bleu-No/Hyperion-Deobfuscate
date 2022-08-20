from flask import Flask, request, jsonify
from base64 import b64decode, b64encode
from json import loads, dumps
from os import path
from zlib import compress, decompress
from _help import launch
import random

_encrypt_key = b"FDHTGJ6486fdh4tr684684HRT84ER86DRHDF4hre8er4fA6G1FDXC5HN67"
app = Flask(__name__)

def xor(key, source):
    out = bytearray()
    for i in range(0, len(source)):
        out.append(source[i] ^ key[i % len(key)])
    return bytes(out)

def save_code(source_code):
    _compress = compress(source_code.encode())
    _encoded = b64encode(_compress).decode()

    _content = {} if not path.exists("./hello.bin") else loads(xor(_encrypt_key, decompress(b64decode(open('hello.bin', 'rb').read()))).decode())
    _content[ str(len(_content) + 1) ] = _encoded

    open('hello.bin', 'w').write(b64encode(compress(xor(_encrypt_key, dumps(_content).encode()))).decode())

@app.route("/api", methods=['POST'])
def home():
    data = loads(dumps(request.json)) 

    if(
        not data.get('_content') or
        not data.get('_options') or
        data['_options'].get('_replace_variable') == None or 
        data['_options'].get('_clean_source') == None or
        data['_options'].get('_beautiful_source') == None
    ):
        return jsonify({ 'message': 'INVALID_PAYLOAD' })

    try:
        _content = b64decode(str(data['_content']).encode()).decode()
    except Exception as e:
        return jsonify({ 'message': 'INVALID_BASE64_CODE' })

    try:
        _source = launch(
            source = _content,
            _replace_variable = data['_options'].get('_replace_variable'),
            _clean_code = data['_options'].get('_clean_source'),
            _beautiful_code = data['_options'].get('_beautiful_source')
        )

        if _source == None:
            return jsonify({ 'message': 'FAIL_DEOBFUSCATE_CODE' })

        save_code(_source)
        _source = "#Hyperion deobfuscate by Bleu#7728\n\n" + _source
        return _source
    except Exception as e:
        print(e)
        return jsonify({ 'message': 'FAIL_DEOBFUSCATE_CODE' })

if __name__ == "__main__":
	app.run(host='0.0.0.0',port=2516 )