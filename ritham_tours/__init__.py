# Apply Python 3.14 compatibility patches
try:
    from . import patches
except ImportError:
    pass
