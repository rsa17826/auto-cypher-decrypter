import itertools
import subprocess
import random
from threading import Thread
from Crypto.Cipher import DES, DES3, AES, ARC4, Blowfish, Salsa20
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from misc import print, f # type:ignore
import sds # type:ignore
from settingsObj import settingsObj
import os
import importlib
from lib import *
from typing import Dict, Any, List
import eel
import csv

# Define the directory where your modules are located
module_directory = "./mods/"
eel.init("web")
# Loop through each file in the directory
modules = {}
for filename in os.listdir(module_directory):
  if filename.endswith(".py") and filename != "__init__.py":
    # Get the module name without the .py extension
    module_name = filename[:-3]
    # Import the module and store it in a dictionary
    module = importlib.import_module(f"mods.{module_name}")
    modules[module_name] = module.exports


# Function to encrypt with DES
def encrypt_des(data):
  key = get_random_bytes(8)
  cipher = DES.new(key, DES.MODE_ECB)
  encrypted_data = cipher.encrypt(pad(data, 8))
  return encrypted_data.hex(), key.hex()


# Function to encrypt with AES
def encrypt_aes(data):
  key = get_random_bytes(16)
  cipher = AES.new(key, AES.MODE_CBC)
  iv = cipher.iv
  encrypted_data = cipher.encrypt(pad(data, 16))
  return encrypted_data.hex(), iv.hex(), key.hex()


# region misc
def json_to_markdown(json_data):
  markdown_lines = []

  # Function to handle dictionary
  def handle_dict(d, level=0):
    for key, value in d.items():
      if isinstance(value, dict):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_dict(value, level + 1)
      elif (
        isinstance(value, list)
        or isinstance(value, tuple)
        or isinstance(key, set)
      ):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_list(value, level + 1)
      else:
        markdown_lines.append("  " * (level) + f"- **{key}:** {value}")

  # Function to handle list
  def handle_list(lst, level=0):
    for key in lst:
      if isinstance(key, dict):
        # markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_dict(key, level + 1)
      elif (
        isinstance(key, list) or isinstance(key, tuple) or isinstance(key, set)
      ):
        markdown_lines.append("  " * (level) + f"- **{key}**")
        handle_list(key, level + 1)
      else:
        markdown_lines.append("  " * (level) + f"- {key}")

  # Start processing
  if isinstance(json_data, dict):
    handle_dict(json_data)
  elif isinstance(json_data, list):
    handle_list(json_data)

  return "\n".join(markdown_lines)


os.makedirs("out", exist_ok=True)


def updateFile(filename, data):
  eel.showOutput(json_to_markdown(data), filename)
  f.write("./out/" + toHex(filename) + ".md", json_to_markdown(data))


# endregion
# region settings
settings: settingsObj = settingsObj(sds.loadDataFromFile("./settings.sds", {}))
# settings: settingsObj = settingsObj({})


## if true will update a partial file after each decryption else will only update the file when all are done
@eel.expose
def requestupdateSettingsUi():
  eel.updateSettingsUi( # type:ignore
    {
      "dontShowErrors": settings.dontShowErrors(True),
      "updateFileEveryDecryption": settings.updateFileEveryDecryption(True),
    }
  )


## if true will hot include the errors in the output files and will not update the file on failed decryptions


# endregion
@eel.expose
def changeSetting(k, v):
  settings[k] = v
  sds.saveDataToFile("./settings.sds", settings)


for file in os.listdir("./out"):
  os.remove("./out/" + file)

# Sample input
input_text = "Hello World"
data = input_text.encode("utf-8")


@eel.expose
def log(*a):
  print(*a)


@eel.expose
def startDecoding(startData: Any) -> None:
  startData = list(filter(lambda x: len(x) > 0, startData)) # type:ignore
  print(startData)
  outputs: Dict[Any, Any] = {
    "MESSAGE": startData[0][0],
  }
  allperms = list(itertools.permutations(startData))
  maxProg = len(allperms) * len(modules)
  prog = 0
  eel.setProg(prog, maxProg) # type:ignore
  for cipherName, funcs in modules.items():
    successes = []
    errors = []
    decrypt = funcs["decrypt"]
    check = funcs["check"]
    format = funcs["format"]
    argCount = funcs["argCount"]
    for encodedDataListpart1 in allperms:
      prog += 1
      eel.setProg(prog, maxProg, cipherName) # type:ignore
      result = set(
        map(lambda x: x[:argCount], itertools.product(*encodedDataListpart1))
      )
      print(result)
      for encodedDataList in result:
        try:
          err = check(encodedDataList)
          if err == 0:

            decrypted_data = decrypt(*format(*encodedDataList))
            decrypted_data = decrypted_data.decode("utf-8", "replace")
            successes.append(
              {
                "dataUsedToDecode": encodedDataList,
                "decrypted_data": decrypted_data,
              }
            )
          else:
            errors.append(err)
        except Exception as e:
          errors.append(f"Failed to decrypt message with {cipherName}: {e}")
        if not (
          (not settings.dontShowErrors(True) and len(errors))
          or (len(successes))
        ):
          continue
        outputs[cipherName] = {}
        if len(successes):
          outputs[cipherName]["successes"] = successes
        if not settings.dontShowErrors(True) and len(errors):
          outputs[cipherName]["errors"] = errors
        if settings.updateFileEveryDecryption(True):
          updateFile("output", outputs)

  if not settings.updateFileEveryDecryption(True):
    updateFile("output", outputs)
  eel.hideProg() # type:ignore


encryption_results = [encrypt_des(data), encrypt_aes(data)]


port = 30068
# random.randint(11111, 65000)
Thread(
  target=lambda: eel.start("main.html", mode=None, port=port, close_callback=os._exit)
).start()

subprocess.run(f'cmd /c "start http://127.0.0.1:{port}/main.html"')

for startData in encryption_results:
  print(startData)

while 1:
  eel.sleep(1)
