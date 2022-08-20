import requests
import base64

api = "https://fuckhyperion.bleuno.repl.co/api"

_file = open('obf.py', 'r').read()
_content = base64.b64encode(_file.encode()).decode()

payload = {
    '_options': {
        '_replace_variable': True,
        '_clean_source': True,
        '_beautiful_source': True
    },
    '_content': _content
}

req = requests.post(api, json = payload)

print(req.text)