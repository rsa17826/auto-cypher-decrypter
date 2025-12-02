from lib import *


def decrypt_des(encrypted_data, key, iv):
  cipher = DES3.new(key, DES3.MODE_CFB, iv=iv)
  return unpad(cipher.decrypt(encrypted_data), 8)


def check(encrypted_data, key, iv):
  if not lenCheck("key", fromHex(key), 16, 24):
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
