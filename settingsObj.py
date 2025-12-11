from typing import Dict, Any, List
from misc import print # type:ignore


class settingsObj:
  def __init__(self, d: Dict = {}):
    print(d)

    def copy(thing, nc=None):
      if nc is None:
        nc = [] if isinstance(thing, list) else {}
      if isinstance(thing, dict):
        for k, v in thing.items():
          nc[k] = copy(v, nc)
      if isinstance(thing, list):
        for v in thing:
          nc.append(copy(v, nc))
      return thing

    self._base = copy(d)

  def __iter__(self):
    return iter(object.__getattribute__(self, "_base"))

  def __setattr__(self, thing, value):
    if thing == "_base":
      object.__setattr__(self, thing, value)
    elif hasattr(self, "_base"):
      # Only set if the base has been initialized
      object.__getattribute__(self, "_base")[thing] = value
    else:
      raise AttributeError(f"'settingsObj' object has no attribute '{thing}'")

  def __getattribute__(self, thing):
    # Avoid infinite recursion by checking if 'thing' is in '_base'
    if thing == "items":
      return object.__getattribute__(self, "_base").items
    if thing == "keys":
      return object.__getattribute__(self, "_base").keys
    if thing == "values":
      return object.__getattribute__(self, "_base").values
    try:
      if thing in object.__getattribute__(self, "_base"):
        value = object.__getattribute__(self, "_base")[thing]
        if isinstance(value, dict) or isinstance(
          value, list
        ): # Only wrap dicts
          return lambda x: settingsObj(value)
        return lambda x: value
    except AttributeError:
      pass
    return lambda x: x

  def __getitem__(self, key):
    return self.__getattribute__(key)

  def __setitem__(self, thing, value):
    if thing == "_base":
      object.__setattr__(self, thing, value)
    elif hasattr(self, "_base"):
      # Only set if the base has been initialized
      object.__getattribute__(self, "_base")[thing] = value
    else:
      raise AttributeError(f"'settingsObj' object has no attribute '{thing}'")
