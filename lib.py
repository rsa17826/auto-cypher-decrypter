from Crypto.Cipher import DES, DES3, AES, ARC4, Blowfish, Salsa20
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from misc import print, f # type:ignore


def fromHex(val: str | bytes) -> bytes:
  if isinstance(val, str):
    return bytes.fromhex(val)
  return val


def toHex(val: str | bytes) -> str:
  if isinstance(val, bytes):
    return val.hex()
  return val


lastLenError = None


def getLenError():
  global lastLenError
  temp = lastLenError
  lastLenError = None
  return temp


def lenCheck(name, val, *lens):
  global lastLenError
  if lastLenError is not None:
    print.error("lastLenError not checked!!!", lastLenError)
  for l in lens:
    if len(val) == l:
      return 1
  lastLenError = (
    f"{name} must be len {lens[0] if len(lens)==1 else ' or '.join(lens)} but is len "
    + str(len(val))
  )
  return 0
