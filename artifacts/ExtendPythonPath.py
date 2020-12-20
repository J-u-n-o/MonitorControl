import sys
import os

# joins the folder to end of path address
address = os.path.dirname(
    os.path.realpath(__file__))

print('{}'.format(sys.path))
print('+{}'.format(address))

sys.path.append(address)
