import os
import sys

# To include the project path in the Operating System path:
print(">>>>>\tAdding project path...")
script_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

