import numbers
from zlib import decompress
from dis import Bytecode
from binascii import unhexlify
from re import match, findall, sub
from requests import post
from string import ascii_lowercase
from random import choice
from tokenize import tokenize, STRING, NUMBER, NAME
from io import BytesIO

number_regex = r'^([0-9_]*)(\+|-)\((\+|-)([0-9_]*)\)$'
replace_regex = r"[A-Za-z0-9]*\([A-Za-z0-9]*\(b'([A-Za-z0-9]*)'\).decode\('8ftu'\[::\+-\+-\(-\(\+1\)\)]\)\)"
filename_regex = r"""if (("[A-Za-z0-9^<>{}\"\/|;:.,~!?@#$%^=&*¿§«»ω⊙¤°℃℉€¥£¢¡®©0-9_+]*")?([wx0-9]*)?([nm0-9]*)?([S0-9]*)?([lI]*)?([oO0-9]*)?([WX0-9]*)?([IJL0-9]*)?([DoO0-9]*)?([NM0-9]*)?([ji0-9]*)):\n *(([wx0-9]*)?([nm0-9]*)?([S0-9]*)?([lI]*)?([oO0-9]*)?([WX0-9]*)?([IJL0-9]*)?([DoO0-9]*)?([NM0-9]*)?([ji0-9]*))\((([wx0-9]*)?([nm0-9]*)?([S0-9]*)?([lI]*)?([oO0-9]*)?([WX0-9]*)?([IJL0-9]*)?([DoO0-9]*)?([NM0-9]*)?([ji0-9]*))\)"""

def object_to_bytecode(code_object):
    return [ _ for _ in Bytecode(code_object) ]

def text_to_object(text):
    name_of_object = "".join([ choice(ascii_lowercase) for i in range(5) ])
    return compile(text, f'<frozen {name_of_object}>', 'exec')

def uncompress(code_object):
    bytecodes = object_to_bytecode(code_object)
    uncompress = b""

    for btc in bytecodes:
        if isinstance(btc.argval, bytes):
            uncompress += btc.argval

    try:
        return decompress(uncompress).decode()
    except:
        return None

def _inverse(text):
    return text[::+-+-(-(+1))]

def remove_credits(text):
    text_split = text.split("\n")

    for index, line in enumerate(text_split):
        if "https://github.com/billythegoat356/Hyperion" in line:
            return "\n".join(text_split[13:])
        
        if index >= 13:
            return text

def invalid_include(line):
    invalid = ['globals', 'dir', 'getattr', 'locals', '__import__', 'builtins', 'join']
    for value in invalid:
        if value in line:
            return True

    return False

def detect_number(text):
    if match(number_regex, text):
        return True
    else:
        return False

def string_to_number(text):
    # data = findall(number_regex, text)[0]
    # number_1 = int(data[0].replace("_", ""))
    # number_2 = int(data[3].replace("_", ""))

    print(eval("4_2_7_0_1_7_9_3_2_4+(-4_2_7_0_1_7_9_3_2_3)"))
    print(eval("1-(-0)"))

    # return text

def detect_type_import(bytecodes):
    if(
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_NAME" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -1
    elif(
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_CONST" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -2

    return -3

def detect_type_variable(bytecodes):
    if(
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_NAME" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -1
    elif (
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_CONST" and
        bytecodes[3].opname == "BINARY_SUBSCR"
    ):
        return -2
    else:
        return -3

def detect_type_content(bytecodes):
    if(
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "LOAD_NAME" and
        bytecodes[2].opname == "LOAD_CONST" and
        bytecodes[3].opname == "CALL_FUNCTION"
    ):
        return -1
    elif (
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_NAME" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -1
    elif (
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "LOAD_CONST" and
        bytecodes[2].opname == "LOAD_CONST" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -2
    elif (
        bytecodes[0].opname == "LOAD_NAME" and
        bytecodes[1].opname == "CALL_FUNCTION" and
        bytecodes[2].opname == "LOAD_CONST" and
        bytecodes[3].opname == "LOAD_CONST"
    ):
        return -4
    else:
        return -3

def find_hex(bytecodes):
    _hex = []
    for btc in bytecodes:
        if isinstance(btc.argval, bytes):
            _hex.append(unhexlify(btc.argval).decode())

    return _hex

def decode_vars(source_code):
    lines = source_code.split('\n')

    claims_variables = {}

    import_modules = ""

    exec_vars = None
    end_variablies = 0

    source_code_filename = ""

    for index, line in enumerate(lines):
        if invalid_include(line):
            continue
        
        if "exec" in line:
            return (claims_variables, import_modules, '\n'.join(lines[(index + 1):]), True)
        elif exec_vars != None and exec_vars in line:
            return (claims_variables, import_modules, '\n'.join(lines[(index + 1):]), True)
        elif "filename=" in line:
            if end_variablies == 0:
                end_variablies = index

            finded = False

            bytecodes = object_to_bytecode(text_to_object(line))
            for btc in bytecodes:
                if isinstance(btc.argval, str):
                    if btc.argval.startswith("))"):
                        u = object_to_bytecode(text_to_object(_inverse(btc.argval)))
                        _sub = find_hex(u)[1]
                        source_code_filename += _sub + "\n"
                        finded = True
                        break

            if not finded:
                u = object_to_bytecode(text_to_object(find_hex(bytecodes)[2]))
                _sub = find_hex(u)[1]
                source_code_filename += _sub + "\n" 

            if (index + 2) == len(lines):
                return (claims_variables, import_modules, source_code_filename, False)

            continue

        if not "=" in line:
            if "cexe" in line:
                continue

            bytecodes = object_to_bytecode(text_to_object(line))
            result = detect_type_import(bytecodes)

            if result == -2 or result == -1:
                
                try:
                    _content = find_hex(bytecodes)[1]
                    if "import" in _content:
                        import_modules += _content + "\n"
                        continue
                except:
                    pass

                for btc in bytecodes:
                    if btc.opname == "LOAD_CONST" and isinstance(btc.argval, str):
                        if not detect_number(_inverse(btc.argval)):
                            if not btc.argval == "8ftu":
                                if not btc.argval in claims_variables:
                                    import_modules += _inverse(btc.argval) + "\n"
                                    
            continue

        variable = object_to_bytecode(text_to_object(line.split('=')[0]))
        content = object_to_bytecode(text_to_object(line.split('=')[1]))

        if "index" in line:
            _variable = variable[2].argval
            
            for index, btc in enumerate(content):
                if btc.opname == "LOAD_METHOD" and btc.argval == "index":
                    _content = _inverse(content[index + 1].argval)

            claims_variables[_variable] = _content
            continue

        result = detect_type_variable(variable)

        if result == -1:
            _variable = find_hex(variable)[0]
        elif result == -2:
            _variable = variable[2].argval
        else:
            _variable = _inverse(variable[2].argval)

        if "lambda" in line:
            claims_variables[_variable] = str(line.split('=')[1]).split(":")[0] + ":locals()"
            continue

        result = detect_type_content(content)
        
        if result == -1:
            _content = find_hex(content)[0]

            if _content == "exec":
                exec_vars = _variable

            if detect_number(_content):
                _content = eval(_content)
        elif result == -2:
            _content = _inverse(content[1].argval)

            if detect_number(_content):
                _content = eval(_content)
        elif result == -4:
            _content = _inverse(content[2].argval)

            if _content == "exec":
                exec_vars = _variable
        else:
            if str(line.split('=')[1]).startswith("not"):
                _content = False
            else:
                _content = True

        claims_variables[_variable] = _content

def inject_variable(claim_variables, encoded_code):
    source_code = ""

    for value in claim_variables:
        source_code += f"{value} = {claim_variables[value]}\n"

    return source_code + "\n" + encoded_code

def replace_variable(claim_variables, encoded_code, lambda_replace):
    _encoded_code_splited = encoded_code.split("\n")

    for _variable in claim_variables:
        for index, _line in enumerate(_encoded_code_splited):
            if _variable in _line:
                if not lambda_replace and "lambda" in str(claim_variables[_variable]):
                    pass
                else:
                    _encoded_code_splited[index] = _line.replace(_variable, str(claim_variables[_variable]))
            
            hello = findall(replace_regex, _line)
            if hello:
                _encoded_code_splited[index] = sub(replace_regex, str(unhexlify(hello[0]).decode()).replace("\\", "\\\\"), _line)

    return "\n".join(_encoded_code_splited)

def clean_code(source, ultra_safe_mode):
    clean_source = source.split('\n')
    clean_code = ""

    name_vars_list =  {}
    index_function_number = 1
    index_variable_number = 1

    index_line = 0

    while True:
        line = clean_source[index_line]
        try:
            _tokens = [ i for i in tokenize(BytesIO(line.encode(), ).readline) ]

            _strings_index = [ (i.string, i.type) for i in _tokens if i.string.strip() != "" ]
            del _strings_index[0]

            if not ultra_safe_mode:
                if len(_strings_index) > 1:
                    if(
                        _strings_index[0][0] == "if" and
                        (
                            _strings_index[1][1] == NAME or
                            _strings_index[1][1] == STRING or
                            _strings_index[1][1] == NUMBER
                        ) and
                        _strings_index[2][0] == ":" and
                        len(_strings_index) == 3
                    ):
                        line_2 = clean_source[index_line + 1]
                        _tokens_2 = [ i for i in tokenize(BytesIO(line_2.encode()).readline) ]
                        _strings_index_2 = [ (i.string, i.type) for i in _tokens_2 if i.string.strip() != "" ]
                        del _strings_index_2[0]

                        if(
                            _strings_index_2[0][1] == NAME and
                            _strings_index_2[1][0] == "(" and
                            (
                                _strings_index_2[2][1] == NAME or
                                _strings_index_2[2][1] == STRING or
                                _strings_index_2[2][1] == NUMBER
                            ) and
                            _strings_index_2[3][0] == ")" and
                            len(_strings_index_2) == 4
                        ):
                            index_line += 2
                            continue

            _temp_var_name = None

            if len(_strings_index) > 1:
                if (_strings_index[0][1] == NAME and _strings_index[1][0] == "="):
                    _temp_var_name = (_strings_index[0][0], "variable")
                elif (_strings_index[0][0] == "def" and _strings_index[1][1] == NAME):
                    _temp_var_name = (_strings_index[1][0], "function")

                if _temp_var_name and not _temp_var_name[0] in name_vars_list:
                    index_number = index_function_number if _temp_var_name[1] == "function" else index_variable_number
                    name_vars_list[_temp_var_name[0]] = f"sub_{_temp_var_name[1]}_{str(index_number)}"
                    
                    if _temp_var_name[1] == "function":
                        index_function_number += 1
                    else:
                        index_variable_number +=1
        except:
            pass

        for v in name_vars_list:
            line = line.replace(v, name_vars_list[v])
        
        clean_code += line + "\n"
        
        index_line +=1
        if index_line >= len(clean_source):
            break

    return clean_code

def beautiful_code(source):
    req = post("https://api.extendsclass.com/python/formatter/auto", data=source)

    if req.status_code == 200:
        return req.text
    else:
        return source

def launch(
    source = None,
    file_path = None,
    _replace_variable = False,
    _clean_code = False,
    _beautiful_code = False
):
    if file_path:
        source = open(file_path, 'r').read()

    objects = compile(source, '<frozen main>', 'exec')
    decompress_code = uncompress(objects)

    if decompress_code:
        _remove_credits = remove_credits(decompress_code)
        _variables, _import_module, _encoded_code, _ultra_safe_mode = decode_vars(_remove_credits)

        if _replace_variable:
            _result = replace_variable(_variables, _import_module + "\n" + _encoded_code, True if not _clean_code else False)
        else:
            _result = _import_module + "\n"
            for value in _variables:
                _result = _result + f"{value} = {_variables[value]};\n"
            _result += "\n\n" + _encoded_code

        if _clean_code:
            _result = clean_code(_result, _ultra_safe_mode)

        if _beautiful_code:
            _result = beautiful_code(_result)

        return _result

    else:
        return None