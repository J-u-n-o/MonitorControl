from pathlib import Path
import sys
import os

# joins the folder to end of path address
address = os.path.dirname(
    os.path.realpath(__file__))

path = Path(__file__).parent


print('  {}'.format(path.parent))
print('  from {}'.format(os.getcwd()))

os.chdir(path.parent)

print('  to   {}'.format(os.getcwd()))
