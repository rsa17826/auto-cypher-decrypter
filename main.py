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
  try:
    eel.showOutput(json_to_markdown(data), filename)
    f.write("./out/" + toHex(filename) + ".md", json_to_markdown(data))
  except Exception as e:
    print.error("error writing file: ", e)


# endregion
# region settings
settings: settingsObj = settingsObj(sds.loadDataFromFile("./settings.sds", {}))


@eel.expose
def requestupdateSettingsUi():
  eel.updateSettingsUi( # type:ignore
    {
      "exitOnPageClose": settings.exitOnPageClose(True),
      ## if true will hot include the errors in the output files and will not update the file on failed decryptions
      "dontShowErrors": settings.dontShowErrors(True),
      ## if true will update a partial file after each decryption else will only update the file when all are done
      "updateOutputEveryDecryption": settings.updateOutputEveryDecryption(True),
      "hideDuplicateErrors": settings.hideDuplicateErrors(True),
      "filterRegex": settings.filterRegex(""),
    }
  )


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


def has_unprintable(data):
  # If it's a string, convert to bytes first
  if isinstance(data, str):
    data = data.encode("utf-8", errors="ignore")
  return any(b < 32 or b > 126 for b in data)


import re


def parseRegex(regStr):
  regFlags = (re.match(r"^[siuoygma]+(?=\))", regStr) or [""])[0]
  regBody = re.sub(r"^[siuoygma]+\)", "", regStr, count=1)
  regFlagsBin = 0
  if "i" in regFlags:
    regFlagsBin |= re.IGNORECASE
  if "m" in regFlags:
    regFlagsBin |= re.MULTILINE
  if "s" in regFlags:
    regFlagsBin |= re.DOTALL
  if "x" in regFlags:
    regFlagsBin |= re.VERBOSE
  if "a" in regFlags:
    regFlagsBin |= re.ASCII
  if "L" in regFlags:
    regFlagsBin |= re.LOCALE
  if "u" in regFlags:
    regFlagsBin |= re.UNICODE
  try:
    return re.compile(regBody, regFlagsBin)
  except re.error as e:
    raise ValueError(f"Invalid regular expression: {e}")


@eel.expose
def startDecoding(startData: Any, message: str | None = None) -> None:
  startData = list(filter(lambda x: len(x) > 0, startData)) # type:ignore
  print(startData)
  outputs: Dict[Any, Any] = {
    "MESSAGE": message if message is not None else startData[0][0],
  }
  try:
    reg = parseRegex(settings.filterRegex(""))
  except Exception as e:
    updateFile("output", {"regex error": f"{e}"})
    return
  allperms = list(itertools.permutations(startData))
  maxProg = len(allperms) * len(modules)
  prog = 0
  eel.setProg(prog, maxProg) # type:ignore
  updateFile("output", {})
  for cipherName, funcs in modules.items():
    successes = []
    errors = []
    decrypt = funcs["decrypt"]
    check = funcs["check"]
    format = funcs["format"]
    argCount = funcs["argCount"]

    if argCount > len(startData) + (1 if message is not None else 0):
      prog += len(allperms)
      eel.setProg(prog, maxProg, cipherName) # type:ignore
      continue

    def adderr(err):
      if err not in errors or not settings.hideDuplicateErrors(True):
        errors.append(err)

    for encodedDataListpart1 in allperms:
      prog += 1
      eel.setProg(prog, maxProg, cipherName) # type:ignore
      result = set(
        map(
          lambda x: (
            (message, *x[: argCount - 1])
            if message is not None
            else x[:argCount]
          ),
          itertools.product(*encodedDataListpart1),
        )
      )
      for encodedDataList in result:
        try:
          err = check(*encodedDataList)
          if err == 0:
            decrypted_data = decrypt(*format(*encodedDataList))
            decrypted_data = decrypted_data.decode("utf-8", "replace")
            if has_unprintable(decrypted_data):
              raise Exception("decrypted_data was not printable")
            if reg.search(decrypted_data):
              successes.append(
                {
                  "dataUsedToDecode": encodedDataList,
                  "decrypted_data": decrypted_data,
                }
              )
            else:
              print(
                "failed to match regex",
                {
                  "dataUsedToDecode": encodedDataList,
                  "decrypted_data": decrypted_data,
                },
              )
          else:
            adderr(err)
        except Exception as e:
          adderr(f"{e}")
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
        if settings.updateOutputEveryDecryption(True):
          updateFile("output", outputs)

  if not settings.updateOutputEveryDecryption(True):
    updateFile("output", outputs)
  eel.hideProg() # type:ignore


encryption_results = []
key = get_random_bytes(24)
iv = get_random_bytes(8)
cipher = DES3.new(key, DES3.MODE_CFB, iv=iv)
print(len(key), len(iv))
encrypted_data = cipher.encrypt(pad(data, 8))
encryption_results.append([encrypted_data.hex(), key.hex(), iv.hex()])
port = 30068
# random.randint(11111, 65000)
Thread(
  target=lambda: eel.start(
    "main.html",
    mode=None,
    port=port,
    close_callback=lambda *x: (
      os._exit(0) if settings.exitOnPageClose(True) else 0
    ),
  )
).start()

subprocess.run(f'cmd /c "start http://127.0.0.1:{port}/main.html"')

for startData in encryption_results:
  print(startData)

while 1:
  eel.sleep(1)
