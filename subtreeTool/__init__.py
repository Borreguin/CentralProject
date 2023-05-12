import os
import sys

# To include the project path in the Operating System path:
script_path = os.path.dirname(os.path.abspath(__file__))
tool_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(tool_path)

