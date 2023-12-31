import os
import argparse

from Code.DataManagement.Quizzing import quiz
from Code.DataManagement.DataHandling import update_scores

from setup import root_dir


def main(args:argparse.Namespace) -> None:
    """
    Function to run the quiz.
    ---
    Args:
    - args (argparse.Namespace): Parsed arguments from the command line.
    Returns:
    - None.
    """
    scores = quiz(root_dir, args.user, args.lang, args.mode, args.common)
    if args.save:
        update_scores(scores)


if __name__ == "__main__":
    available_languages = [lang.lower() for lang in os.listdir(f'{root_dir}/Material')]
    available_modes = ['conjugations', 'vocabulary']
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", help="Select language to be practiced.", type=str, choices=available_languages)
    parser.add_argument("--mode", help="Determines what the quiz will be about.", type=str, choices=available_modes)
    parser.add_argument("--save", help="Record results from this quiz.", action='store_true', default=False)
    parser.add_argument("--user", help="User where the records will be saved.", type=str, default=None)
    parser.add_argument("--word", help="Ask this word/verb in particular.", type=str, default=None)
    parser.add_argument("--common", help="Ask only common words.", action='store_true', default=False)
    args = parser.parse_args()

    # Check arguments.
    if args.lang is None:
        raise ValueError(f"ERROR -- You must specify a language with the flag '--lang <LANG>'.")
    separator = "', '"
    if args.lang not in available_languages:
        raise ValueError(f"ERROR -- Language '{args.lang}' not found. Available languages are '{separator.join(available_languages)}'.")
    
    if args.mode is None:
        raise ValueError(f"ERROR -- You must specify a mode with the flag '--mode <MODE>'.")
    if args.mode not in available_modes:
        raise ValueError(f"ERROR -- Mode '{args.mode}' not found. Available languages are '{separator.join(available_modes)}'.")
    
    if args.save and args.user is not None:
        raise ValueError("ERROR -- Need to provide a user if you want to save.")
    
    if args.word is not None and args.common:
        args.common = False
        raise ValueError("WARNING -- The --common flag is ignored if a word is given.")
    try:
        error = True
        main(args)
        error = False
    except KeyboardInterrupt:
        error = False
        print('\nQuiz stopped by user.')
    except Exception as exception:
        raise ValueError(f"\rERROR -- An error occured during the realization of the quiz: {exception}")
    finally:
        print("Quiz finished successfully.") if not error else print("Quiz has been aborted.")