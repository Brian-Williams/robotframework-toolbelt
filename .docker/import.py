import importlib
from robottools import __title__


globals()[__title__] = importlib.import_module(__title__)
print('"{}" imported'.format(__title__))
