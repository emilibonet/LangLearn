import re
import os
import json
from glob import glob  # Find files with patterns.

try: 
    from DataHandling import get_overall_scores, update_scores
except ModuleNotFoundError:
    from Code.DataManagement.DataHandling import get_overall_scores, update_scores


YELLOW, GREEN, RED, GREY, LILOS, MAGENTA = '#fcd853', '#75f73e', '#ff0000', '#707070', '#6957cf', '#8c008c'
BOLDFACE, CURSIVE, UNDERLINED, CROSSEDOUT = '\x1b[1m', '\x1b[3m', '\x1b[4m', '\033[9m'

def color_formatter(color):
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

def style_formatter(style):
    style_dict = {'boldface':BOLDFACE, 'cursive':CURSIVE, 'underlined':UNDERLINED, 'crossed-out':CROSSEDOUT}
    if style in style_dict.keys():
        return style_dict[style]
    elif style in style_dict.values():
        return style
    else:
        raise ValueError(f"Font style '{style}' is not supported.")


def printf(text:str, color=None, style:str=None, linesup:int=0, end:str='\n') -> None:
    style_prefix = style_formatter(style) if style is not None else ''
    color_prefix = color_formatter(color) if color is not None else ''
    resetting_suffix = '\033[0m' if style is not None or color is not None else ''
    print('\033[1A'*linesup+'\033[K'+color_prefix+style_prefix+text+resetting_suffix, end=end)


def ask(question:str=None, default:str=None):
    if default is not None and not default.lower() in ['y', 'n']:
        raise ValueError(f"Incorrect default value '{default}'. Must be either 'y' or 'n'.")
    while True:
        printf(question + f" ({'[y]' if default == 'y' else 'y'}/{'[n]' if default == 'n' else 'n'})?", color=GREY, end=' ')
        skip = input().lower()
        printf('', linesup=1, end='')
        if skip in ['y', 'n']:
            return skip == 'y'
        if skip == '' and default is not None:
            return default.lower() == 'y'


def conjugations_quiz(conjugation:dict):
    verb_score = {}
    for tense_group in conjugation:
        if tense_group == 'Translation':
            continue
        printf(tense_group, style='boldface', color=YELLOW)
        verb_score[tense_group] = {}
        for tense in conjugation[tense_group]:
            printf(tense, style='cursive', color=YELLOW)
            verb_score[tense_group][tense] = [[] for _ in conjugation[tense_group][tense]]         
            skip_tense = ask('Skip tense', default='n')
            if skip_tense:
                continue
            if tense_group == 'Nominal Forms':
                printf(tense, style='cursive', color=GREY, end=' - ')
                answer = input().lower()
                is_correct = answer == conjugation[tense_group][tense][0]
                verb_score[tense_group][tense].append(int(is_correct))
                printf('', linesup=1, end='')
                printf(tense, style='cursive', color=GREY, end=' - ')
                if not is_correct:
                    printf(answer if answer else '(none)', color=RED, style='crossed-out', end=' ')
                printf(conjugation[tense_group][tense][0], color=GREEN, end='')
                if len(conjugation[tense_group][tense]) > 1:  # Has pronounciation.
                    printf(' ' + conjugation[tense_group][tense][1], color=LILOS)
                else:
                    print()
            else:
                max_subj_len = max([len(subj) for subj,_,_ in [verb for verb in conjugation[tense_group][tense]]])
                try:
                    answers, is_correct, loop_type = [], [], 0
                    while loop_type < 3:
                        for i in range(len(conjugation[tense_group][tense])):
                            if loop_type > 0 and i == 0:
                                printf('', linesup=len(conjugation[tense_group][tense]), end='')
                            printf(f"{' '*max(0, max_subj_len-len(conjugation[tense_group][tense][i][0]))}{conjugation[tense_group][tense][i][0]} ", end='')
                            if loop_type == 0: # Print all.
                                print()
                            elif loop_type == 1:  # Gather input.
                                answer = input().lower()
                                answers.append(answer)
                                is_correct.append(answer == conjugation[tense_group][tense][i][1])
                                verb_score[tense_group][tense][i] = int(is_correct[i])
                            elif loop_type == 2:  # Print corrections.
                                if not is_correct[i]:
                                    printf(answers[i] if answers[i] else '(none)', color=RED, style='crossed-out', end=' ')
                                printf(conjugation[tense_group][tense][i][1], color=GREEN, end='')
                                if conjugation[tense_group][tense][i][2] != '<NA>':
                                    printf(' ' + conjugation[tense_group][tense][i][2], color=LILOS)
                                else:
                                    print()
                        loop_type += 1
                except KeyboardInterrupt:
                    if ask("Redo current tense"):
                        answers, is_correct, loop_type = [], [], 0
                        print(f'\x1b[{6}B', end='')
                    elif ask("Skip tense"):
                        ...
    return verb_score


def vocabulary_quiz(vocabulary:dict):
    print(vocabulary)
    word_score = {}
    return word_score


def display_translation(material, mode) -> None:
    if mode not in ['conjugations', 'vocabulary']:
        raise ValueError(f"ERROR -- Unknown mode '{mode}'.")
    # TODO: Finish the translation for vocabulary mode<
    translation = material['Translations']['Translations'] if mode == 'conjugations' else None
    if len(translation) == 1 and translation[0] == list(material['Nominal Forms'].values())[0][0]:  # This position contains the infinitive.
        printf(f"(No translations available)", color=GREY)
    else:
        for idx, entry in enumerate(translation):
            printf(f"({idx+1})", color=GREY, end=' ')
            print(entry)



def quiz(root_dir:str, user:str, lang:str, mode:str, freq:bool=False, word:str=None):
    if mode not in ['conjugations', 'vocabulary']:
        raise ValueError(f"\rERROR -- Mode '{mode}' is unknown.")

    # Get either conjugations or vocabulary set depending on the mode.
    with open(os.path.join(root_dir, f"Material/{lang}/{mode}.json")) as material_file:
        material = json.load(material_file)
    if freq:
        keyword = 'infinitives' if mode == "conjugations" else 'words'
        with open(glob(os.path.join(root_dir, f"Material/{lang}/.{keyword}*frequent.json"))[0]) as freq_file:
          freq_list = json.load(freq_file)

    overall_scores = sorted(get_overall_scores(root_dir, lang, user, mode).items(), key=lambda x:x[1])

    # If user gave a specific word to be quizzed about, use that word.
    if word is not None:
        if word in overall_scores.keys():
            overall_scores = overall_scores[word]
        else:
            raise ValueError(f"\rERROR -- Word '{word}' is not present in {mode} set.")
    
    # Start the quiz.
    try:
        scores = {}
        for word, existing_score in overall_scores:
            if word in material.keys() and (not freq or word in freq_list):
                grade_str = f' (current grade: {round(existing_score*10, 2)}/10)' if user is not None else ''
                printf(f"{'Verb' if mode == 'conjugations' else 'Word'} '{word.capitalize()}'{grade_str}", color=MAGENTA, style='boldface')
                display_translation(material[word], mode)
                skip_verb = ask('Skip verb', default='n')
                if not skip_verb:
                    scores[word] = globals()[mode+'_quiz'](material[word])
        update_scores(root_dir, lang, user, mode, scores) if user is not None else None
    except KeyboardInterrupt:
        update_scores(root_dir, lang, user, mode, scores) if user is not None else None
        raise KeyboardInterrupt
