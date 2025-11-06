import Crypto.Cipher.DES as DES
import Crypto.Cipher.DES3 as DES3
import Crypto.Cipher.PKCS1_OAEP as PKCS1_OAEP
import Crypto.Cipher.PKCS1_v1_5 as PKCS1_v1_5
import Crypto.Cipher.Salsa20 as Salsa20
import Crypto.Cipher.AES as AES
import Crypto.Cipher.ARC2 as ARC2
import Crypto.Cipher.ARC4 as ARC4
import Crypto.Cipher.Blowfish as Blowfish
import Crypto.Cipher.CAST as CAST
import Crypto.Cipher.ChaCha20 as ChaCha20
import Crypto.Cipher.ChaCha20_Poly1305 as ChaCha20_Poly1305

cypherList = [
  DES,
  DES3,
  PKCS1_OAEP,
  PKCS1_v1_5,
  Salsa20,
  AES,
  ARC2,
  ARC4,
  Blowfish,
  CAST,
  ChaCha20,
  ChaCha20_Poly1305,
]
