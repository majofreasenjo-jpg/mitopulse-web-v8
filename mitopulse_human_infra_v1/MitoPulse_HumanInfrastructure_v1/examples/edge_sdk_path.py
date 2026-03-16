
import os, sys
def add_sdk_path():
    root = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, root)
