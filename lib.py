from Crypto.Cipher import DES, DES3, AES, ARC4, Blowfish, Salsa20
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from misc import print, f


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

