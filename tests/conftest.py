import os
import sys

# Agregar la raíz del proyecto al sys.path para importaciones de módulos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
