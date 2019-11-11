import sys
from utils.Core import PyGUIno


if __name__ == "__main__":

    try:
        pygu = PyGUIno()
        pygu.start()
    except Exception as err:
        print(err)
