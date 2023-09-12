import os
import argparse
from time import time

import Code.DataManagement.DataHandling as dh

root_dir = os.path.dirname(os.path.realpath(__file__))


def report_time(total_seconds:int) -> str:
    """
    Used to convert seconds to a human-readable format.

    Arguments:
        - total_seconds (int): The total number of seconds.

    Returns:
        - A human-readable format.
    """
    if total_seconds < 5e-3:
        return f'{round(total_seconds * 1000, 4)} ms'
    hours, minutes, seconds = int(total_seconds // 3600), int((total_seconds % 3600) // 60), round(total_seconds % 60, 2)
    res = []
    if hours > 0:
        res.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        res.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        res.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ' '.join(res)
    


def setup(args:argparse.Namespace) -> None:
    """
    Entry point to organize the data in the project.

    ---
    Arguments:
        - args (argparse.Namespace): The arguments from the command line.
    
    Returns:
        - None
    """
    supported_languages = os.listdir(os.path.join(root_dir, 'Material')) if args.lang == 'all' else [args.lang]
    for lang in supported_languages:
        Lang = lang.capitalize()
        if dh.verify_data_structure(root_dir, lang):
            print(f"Data structure amended during verification for {Lang}.")
        
        if args.mode == 'verbs':
            print(f"Setting up the verb corpus for {Lang}...")
            start = time()
            dh.create_verbal_corpus(root_dir, lang, args.force)
            print(f"Setting up the verb corpus for {Lang} -- completed in {report_time(time()-start)}.")
        elif args.mode == 'addword':
            print(f"Adding word '{args.newword}' to the {Lang} vocabulary corpus...", end="\r")
            start = time()
            dh.add_vocab(root_dir, lang, args.newword, args.force)
            print(f"Adding word '{args.newword}' to the {Lang} vocabulary corpus -- completed in {report_time(time()-start)}.")
        elif args.mode == 'adduser':
            print(f"Adding user '{args.username}'...")
            start = time()
            if dh.add_user(root_dir, lang, args.username, args.force):
                print(f"User {args.username} was successfully created.")
            print(f"Adding user '{args.username}' -- completed in {report_time(time()-start)}.")
        else:
            raise ValueError(f"Mode argument '{args.mode}' is unknown.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", help="Select language to be set up. If None, all will be created.",
                        type=str, choices=['french', 'german', 'occitan'], default=None)
    parser.add_argument('--force', help="Ignores existing material, creating the data from scratch.", action='store_true')
    parser.add_argument("--mode", help="'verbs' will collect verbal material for the language specified.\
                                        'addword' will add this word into the vocabulary corpus for the language specified.\
                                        'adduser' will create a scores json for the user specified.",
                        type=str, choices=['verbs', 'addword', 'adduser'], default=None)
    parser.add_argument("--username", help="Creates scores for a username indicated in the passed argument.",
                        type=str, default=None)
    parser.add_argument("--newword", help="Adds the passed word to the vocabulary corpus.", 
                        type=str, default=None)
    args = parser.parse_args()

    if args.mode == 'adduser' and args.username is None:
        raise ValueError("\rERROR -- If 'adduser' mode is selected, a username must be specified.")
    if args.mode == 'addword' and args.newword is None:
        raise ValueError("\rERROR -- If 'addword' mode is selected, a word must be specified.")
    try:
        setup(args)
        print("Ended successfully!")
    except Exception as err:
        print(f"\nABORTED:\n{err}")