from lib import *


def decrypt_aes(encrypted_data, iv, key):
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return unpad(cipher.decrypt(encrypted_data), 16)


exports = {
  "decrypt": decrypt_aes,
  "check": lambda data: "must have 3 values" if len(data) != 3 else 0,
  "format": lambda encrypted_data, iv, key: [
    fromHex(encrypted_data),
    fromHex(iv),
    fromHex(key),
  ],
}
