import hashlib
import base64
import json


def calchash(text):
    filecontents = text.encode('utf-8')
    md5hash = hashlib.md5(filecontents).hexdigest()

    return md5hash



def encode(din):
    din_bytes = din.encode('utf-8')
    base64_bytes = base64.b64encode(din_bytes)
    return base64_bytes.decode('utf-8')


def decode(din):
    din_bytes = din.encode('utf-8')
    base64_bytes = base64.b64decode(din_bytes)
    return base64_bytes.decode('utf-8')


def safesave(data):
    with open("save/savegame.json", "w") as f:
        json.dump(data, f)

    print("Game saved!")

    with open("save/savegame.json", "r") as f:
        with open("save/.savefile.txt", "w") as s:
            s.write(encode(f.read()))
    with open ("save/.savefile.txt", "r") as f:
        with open("save/.hash.txt", "w") as s:
            s.write(calchash(f.read()))

def safeload():

    with open ("save/.savefile.txt", "r") as f:
        with open("save/.hash.txt", "r") as s:
            if s.read() != calchash(f.read()):

                return False

    with open("save/.savefile.txt", "r") as f:
        encoded_data = f.read()
        decoded_data = decode(encoded_data)
        data = json.loads(decoded_data)
        return data