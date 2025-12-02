from lib import *


def decrypt_des(encrypted_data, key):
  cipher = DES3.new(key, DES3.MODE_OPENPGP)
  return unpad(cipher.decrypt(encrypted_data), 8)


def check(data):
  key = data[0]
  msg = data[1]
  if len(fromHex(key)) != 24 and len(fromHex(key)) != 16:
    return "key must be len 24 or 16 but is len " + str(len(fromHex(key)))

  return 0


exports = {
  "decrypt": decrypt_des,
  "argCount": 2,
  "check": check,
  "format": lambda encrypted_data, key: [fromHex(encrypted_data), fromHex(key)],
}
