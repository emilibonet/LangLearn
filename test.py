import re
from time import time, sleep

def ascii_color(color):
    if type(color) == int:
        color = str(color)
    if type(color) == str:
        if re.match('#?[A-Fa-f0-9]{6}', (color := color.strip('#'))) is None:
            raise ValueError(f"Color '{color}' has invalid HEX color format.")
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    elif type(color) in [tuple, list]:
        is_rbg_int = lambda integer: type(integer) == int and 0 <= integer and integer <= 255
        if len(color) != 3 and not (is_rbg_int(color[0]) and is_rbg_int(color[1]) and is_rbg_int(color[2])):
            raise ValueError(f"Color '{', '.join(color)}' has invalid RGB color format.")
    else:
        raise ValueError(f"Color format of '{color}' is unknown. Use RGB (tuple/list) or HEX (str/int).")
    return f"\033[38;2;{';'.join([str(x) for x in color])}m"

def printf(text:str, color=None, linesup:int=0, end:str='\n') -> None:
    color_prefix, color_suffix = (ascii_color(color) , '\033[0m') if color is not None else ('', '')
    print('\033[1A'*linesup+'\033[K'+color_prefix+text+color_suffix, end=end)

if __name__ == '__main__':
    printf("Aquesta és una línia d'entrada: ", end='')
    entrada = input()
    print("Alguna altra cosa.")
    sleep(3)
    printf("Aquesta és una línia d'entrada: ", linesup=2, end='')
    printf(entrada, color='#168bd9')