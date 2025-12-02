from lib import *


def decrypt_aes(encrypted_data, key, iv):
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return unpad(cipher.decrypt(encrypted_data), 16)


def check():
  return 0


exports = {
  "decrypt": decrypt_aes,
  "argCount": 3,
  "check": check,
  "format": lambda encrypted_data, key, iv: [
    fromHex(encrypted_data),
    fromHex(key),
    fromHex(iv),
  ],
}
