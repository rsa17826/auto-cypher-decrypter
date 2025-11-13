from lib import *


def decrypt_des(encrypted_data, key):
  cipher = DES.new(key, DES.MODE_ECB)
  return unpad(cipher.decrypt(encrypted_data), 8)


exports = {
  "decrypt": decrypt_des,
  "argCount":2,
  "check": lambda data: "must have 2 values" if len(data) != 2 else 0,
  "format": lambda encrypted_data, key: [fromHex(encrypted_data), fromHex(key)],
}
