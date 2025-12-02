from lib import *


def decrypt_des(encrypted_data, key, iv):
  cipher = DES3.new(key, DES3.MODE_OFB, iv=iv)
  return unpad(cipher.decrypt(encrypted_data), 8)


def check(data):
  key = data[0]
  msg = data[1]
  if not lenCheck("key", fromHex(key), 16, 24):
    return getLenError()
  if not lenCheck("iv", fromHex(iv), 8):
    return getLenError()

  return 0


exports = {
  "decrypt": decrypt_des,
  "argCount": 3,
  "check": check,
  "format": lambda encrypted_data, key, iv: [
    fromHex(encrypted_data),
    fromHex(key),
    fromHex(iv),
  ],
}
