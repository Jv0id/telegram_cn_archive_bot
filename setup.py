import os
import sys


def kill():
    os.system("ps aux | grep ython | grep archive.py | awk '{print $2}' | xargs kill -9")


def setup():
    kill()
    if 'kill' in sys.argv:
        return

    os.chdir(sys.path[0])

    os.system('rm -f nohup.out')

    RUN_COMMAND = "nohup python3 -u archive.py &"

    if 'debug' in sys.argv:
        os.system(RUN_COMMAND[6:-2])
    else:
        os.system(RUN_COMMAND)
        if 'notail' not in sys.argv:
            os.system('touch nohup.out && tail -F nohup.out')


if __name__ == '__main__':
    setup()
