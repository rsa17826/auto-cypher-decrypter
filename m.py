from Crypto.Cipher import DES, DES3, AES, ARC4, Blowfish, Salsa20
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from misc import print, f

# Sample input
input_text = "Hello World"
data = input_text.encode("utf-8")


# Function to encrypt with DES
def encrypt_des(data):
  key = get_random_bytes(8)
  cipher = DES.new(key, DES.MODE_ECB)
  encrypted_data = cipher.encrypt(pad(data, 8))
  return encrypted_data.hex(), key.hex()


def decrypt_des(encrypted_data, key):
  cipher = DES.new(key, DES.MODE_ECB)
  return unpad(cipher.decrypt(encrypted_data), 8)


# Function to encrypt with AES
def encrypt_aes(data):
  key = get_random_bytes(16)
  cipher = AES.new(key, AES.MODE_CBC)
  iv = cipher.iv
  encrypted_data = cipher.encrypt(pad(data, 16))
  return encrypted_data.hex(), iv.hex(), key.hex()


def decrypt_aes(encrypted_data, iv, key):
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return unpad(cipher.decrypt(encrypted_data), 16)


# Encrypting "Hello World" with each cipher
encryption_results = {
  "DES": encrypt_des(data),
  "AES": encrypt_aes(data),
}


def fromHex(val: str | bytes) -> bytes:
  if isinstance(val, str):
    return bytes.fromhex(val)
  return val


def toHex(val: str | bytes) -> str:
  if (
    isinstance(val, bytes)
    or isinstance(val, memoryview)
    or isinstance(val, bytearray)
  ):
    return val.hex()
  return val


def json_to_markdown(json_data):
  markdown_lines = []

  # Function to handle dictionary
  def handle_dict(d, level=0):
    for key, value in d.items():
      if isinstance(value, dict):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_dict(value, level + 1)
      elif isinstance(value, list) or isinstance(value, tuple):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_list(value, level + 1)
      else:
        markdown_lines.append("  " * (level) + f"- **{key}:** {value}")

  # Function to handle list
  def handle_list(lst, level=0):
    for key in lst:
      if isinstance(key, dict):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_dict(key, level + 1)
      elif isinstance(key, list) or isinstance(key, tuple):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_list(key, level + 1)
      else:
        markdown_lines.append("  " * (level) + f"- {key}")

  # Start processing
  if isinstance(json_data, dict):
    handle_dict(json_data)
  elif isinstance(json_data, list):
    handle_list(json_data)

  return "\n".join(markdown_lines)


ciphers = [
  [
    "AES",
    decrypt_aes,
    lambda data: "must have 3 values" if len(data) != 3 else 0,
    lambda encrypted_data, iv, key: [
      fromHex(encrypted_data),
      fromHex(iv),
      fromHex(key),
    ],
  ],
  [
    "DES",
    decrypt_des,
    lambda data: "must have 2 values" if len(data) != 2 else 0,
    lambda encrypted_data, key: [fromHex(encrypted_data), fromHex(key)],
  ],
]


def updateFile(filename, data):
  f.write("./out/" + toHex(filename) + ".md", json_to_markdown(data))

## if true will update a partial file after each decryption else will only update the file when all are done
updateFileEveryDecryption = True
## if true will hot include the errors in the output files and will not update the file on failed decryptions
dontShowErrors = True

for origenc, result in encryption_results.items():
  outputs = {"MESSAGE": result, "origenc": origenc}
  for cipherName, cipher, canUseThisCipher, formatData in ciphers:
    try:
      err = canUseThisCipher(result)
      if err == 0:
        decrypted_data = cipher(*formatData(*result))
        decrypted_data = decrypted_data.decode("utf-8", "replace")
        outputs[cipherName] = {"success": decrypted_data}
        if updateFileEveryDecryption and dontShowErrors:
          updateFile(result[0], outputs)
      else:
        outputs[cipherName] = {"error": err}
    except Exception as e:
      # continue
      outputs[cipherName] = {
        "error": f"Failed to decrypt {origenc} with {cipherName}: {e}"
      }
    if updateFileEveryDecryption and not dontShowErrors:
      updateFile(result[0], outputs)

  if not updateFileEveryDecryption:
    updateFile(result[0], outputs)
