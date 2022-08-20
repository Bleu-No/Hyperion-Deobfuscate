from base64 import b64encode
from zlib import compress
from string import ascii_letters
from random import choice
import os

_key = b"456DFRH45DR6TH446fd4rst68h46f8gh4684B864B8NB4RT89BS6D484df86h48rth"
_default_code = """
globals()['#VAR'] = getattr(getattr(__builtins__, '__import__')('zlib'), 'decompress')(getattr(getattr(__builtins__, '__import__')('base64'), 'b64decode')(b"#CODE"))
getattr(__builtins__, 'exec')(bytes([(globals()['#VAR'][i] ^ str(getattr(getattr(__builtins__, '__import__')('os'), 'environ')['_key']).encode()[i % len(str(getattr(getattr(__builtins__, '__import__')('os'), 'environ')['_key']).encode())]) for i in range(0, len(globals()['#VAR'])) ]))
"""

_import_code = """
globals()['#VAR'] = getattr(__builtins__['__import__']('zlib'), 'decompress')(getattr(__builtins__['__import__']('base64'), 'b64decode')(b"#CODE"))
__builtins__['exec'](bytes([(globals()['#VAR'][i] ^ str(getattr(__builtins__['__import__']('os'), 'environ')['_key']).encode()[i % len(str(getattr(__builtins__['__import__']('os'), 'environ')['_key']).encode())]) for i in range(0, len(globals()['#VAR'])) ]))
"""

def xor(key, source):
    out = bytearray()
    for i in range(0, len(source)):
        out.append(source[i] ^ key[i % len(key)])
    return bytes(out)

def encrypt(source, _type = 0):
    _xored = xor(_key, source.encode())
    _compress = compress(_xored)
    _encoded = b64encode(_compress).decode()

    _code = _default_code if _type == 0 else _import_code
    _code = _code.replace("#VAR", "".join([ choice(ascii_letters) for i in range(16) ]))
    _code = _code.replace("#CODE", _encoded)
    _code = _code.replace("#KEY", _key.decode())

    return _code

if __name__ == "__main__":
    files = [ open('server.py', 'r').read(), open('_help.py', 'r').read() ]

    os.mkdir('dist')

    _result = encrypt(files[0], 0)
    _result2 = encrypt(files[1], 1)

    open('./dist/main.py', 'w').write(_result)
    open('./dist/_help.py', 'w').write(_result2)