import sys
import os

def convert_to_utf8_no_bom(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    convert_to_utf8_no_bom(sys.argv[1])