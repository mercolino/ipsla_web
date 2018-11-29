import random
import string
import argparse
import os.path


def save_to_file(pwd):
    f = open('_usr.p', 'wb')
    f.write(pwd.encode('ascii'))
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('passphrase', help='Passphrase to save use double quotes for passphrases with spaces')

    args = parser.parse_args()

    if os.path.isfile('_usr.p'):
        print('Password file already generated, Passphrase not saved!')
    else:
        save_to_file(args.passphrase)
