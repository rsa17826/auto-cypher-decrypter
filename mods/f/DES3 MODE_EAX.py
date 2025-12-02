from lib import *


def decrypt_des(encrypted_data, key):
  cipher = DES3.new(key, DES3.MODE_EAX)
  return cipher.decrypt(encrypted_data)


def check(data):
  key = data[0]
  msg = data[1]
  if not lenCheck("key", fromHex(key), 16, 24):
    return getLenError()
  return 0


exports = {
  "decrypt": decrypt_des,
  "argCount": 2,
  "check": check,
  "format": lambda encrypted_data, key: [fromHex(encrypted_data), fromHex(key)],
}
