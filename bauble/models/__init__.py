from os.path import dirname, basename, isfile
import glob
from importlib import import_module
from inspect import isclass
import sys

import bauble.db as db

# import all model subclasses in this package
modules = glob.glob(dirname(__file__) + "/*.py")
for filename in modules:
    if not isfile(filename) or filename == __file__:
        continue
    module_name = basename(filename)[:-3]
    mod = import_module('.{}'.format(module_name), __package__)
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if isclass(attr) and issubclass(attr, db.Model):
            setattr(sys.modules[__name__], attr_name, attr)
