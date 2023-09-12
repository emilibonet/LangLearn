import os
import json

import Code.DataManagement.DataCollection as dc


def verify_data_structure(root_dir:str, lang:str) -> bool:
    """
    Checks if the data structure is correct. If it is not, it makes the necessary amends.

    ---
    Arguments:
    - root_dir (str): The root directory of the project.
    - lang (str): The language in question.

    Returns:
    - bool: True if the data structure is correct, False if changes were made.
    """

    changes_done = False
    if not os.path.exists(os.path.join(root_dir, 'Material')):
        os.makedirs(os.path.join(root_dir, 'Material'))
        changes_done = True
    if not os.path.exists(os.path.join(root_dir, 'Material', lang)):
        os.makedirs(os.path.join(root_dir, 'Material', lang))
        changes_done = True
    if not os.path.exists(os.path.join(root_dir, 'Material', lang, 'users')):
        os.makedirs(os.path.join(root_dir, 'Material', lang, 'users'))
        changes_done = True
    if not os.path.isfile(os.path.join(root_dir, 'Material', lang, '.infinitives-complete.json')):
        raise Exception(f"'.infinitives-complete.json' not found for {lang}. Please download it from the original repository and put it in {os.path.join(root_dir, 'Material', lang)}.")
    return changes_done


def create_verbal_corpus(root_dir:str, lang:str, force:bool=False) -> None:
    """
    Creates the material for the given language.

    Arguments:
    - root_dir (str): The root directory of the project.
    - lang (str): The language in question.
    - force (bool): If True and the collector finds verbs that already exist in the corpus, it will overwrite the existing record.

    Returns:
    - None
    """

    conjugation_collector = dc.ConjugationCollector(root_dir)
    conjugations, scores, uncatched_verbs = conjugation_collector.collect(lang, force)
    if len(uncatched_verbs):
        print(f"WARNING -- Unable to collect conjugations for the following verbs: {', '.join(uncatched_verbs)}.")

    print(f"Storing the conjugations and initializing scores in the database for {lang.capitalize()}...", end="\r")
    with open(os.path.join(root_dir, 'Material', lang, 'conjugations.json'), 'w') as conjugations_file:
        json.dump(conjugations, conjugations_file, indent=2)
    with open(os.path.join(root_dir, 'Material', lang, '.conjscores-template.json'), 'w') as conjscores_file:
        json.dump(scores, conjscores_file, indent=2)


def add_vocab(root_dir:str, lang:str, newword:str, force:bool=False) -> None:
    """
    Adds a new word to the vocabulary list.

    ---
    Arguments:
    - root_dir (str): The root directory of the project.
    - lang (str): The language in question.
    - newword (str): The new word to be added.
    - force (bool): If True and word exists, will overwrite the existing record.

    Returns:
    - None.
    """
    vocabulary_collector = dc.VocabularyCollector(root_dir)
    vocabulary, scores = vocabulary_collector.collect(newword, lang, force)

    print(f"Storing the conjugations and initializing scores in the database for {lang.capitalize()}...", end="\r")
    with open(os.path.join(root_dir, 'Material', lang, 'vocabulary.json'), 'w') as vocabulary_file:
        json.dump(vocabulary, vocabulary_file, indent=2)
    with open(os.path.join(root_dir, 'Material', lang, '.vocabscores-template.json'), 'w') as vocabscores_file:
        json.dump(scores, vocabscores_file, indent=2)


def acknowledged_erase() -> bool:
    """
    Notifies the user if they are sure they want to erase the scores.

    ---
    Arguments:
    - (None)

    Returns:
    - bool: True if the user confirms they want to erase the scores, False otherwise.
    """
    while True:
        response = input("Are you sure you want to erase the existing scores? THIS ACTION CANNOT BE REVERSED! (y/n): ").lower()
        if response in ['y', '']:
            return True
        elif response == "n":
            return False
        else:
            print("Please input 'y' (yes) or 'n' (no).")


def add_user(root_dir:str, lang:str, username:str, force:bool=False) -> bool:
    """
    Creates a user score file for the given language.

    ---
    Arguments:
    - root_dir (str): The root directory of the project.
    - lang (str): The language in question.
    - username (str): The name of the user to be added.
    - force (bool): If True and user exists, will overwrite the existing scores for that user.

    Returns:
    - bool: True if the user score file was created, False otherwise.
    """
    try:
        newuser = [
            os.path.join(root_dir, 'Material', lang, 'users', f'conjscores-{username}.json'),
            os.path.join(root_dir, 'Material', lang, 'users', f'vocabscores-{username}.json')
        ]
        if not os.path.isfile(newuser[0]) or (force and acknowledged_erase()):
            os.system(f"cp {os.path.join(root_dir, 'Material', lang, '.conjscores-template.json')} {newuser[0]}")
            os.system(f"cp {os.path.join(root_dir, 'Material', lang, '.vocabscores-template.json')} {newuser[1]}")
            return True
        elif not force:
            print(f"User {username} already exists. Use --force option to re-do the user scores file.")
        else:
            print("User creation was aborted.")
        return False
    except Exception as err:
        print(f"\rERROR -- Unable to create user {username}: {err}")
        return False


def get_overall_scores(root_dir:str, lang:str, user:str, mode:str) -> dict:
    """
    Provides the overall score of a user for a given language and mode.

    ---
    Arguments:
    - root_dir (str): The main directory of the project.
    - lang (str): The language in question.
    - user (str): The user in question.
    - mode (str): The mode in question; either 'conjugations' or 'vocabulary'.

    Returns:
    - dict: A dictionary with the overall scores.
    """
    overall_scores, shortened_mode = {}, {'conjugations':'conj', 'vocabulary':'vocab'}[mode]
    file = f"users/{shortened_mode}scores-{user}.json" if user is not None else '.conjscores-template.json'
    with open(os.path.join(root_dir, 'Material', lang, file), 'r') as scores_file:
        scores = json.load(scores_file)
    if mode == 'conjugations':
        for verb in scores:
            verb_score = 0
            for tense_group in scores[verb]:
                for tense in scores[verb][tense_group]:
                    for i in range(len(scores[verb][tense_group][tense])):
                        verb_score += sum(scores[verb][tense_group][tense][i])/len(scores[verb][tense_group][tense][i]) if len(scores[verb][tense_group][tense][i]) else 0
            overall_scores[verb] = verb_score
        return overall_scores
    if mode == 'vocabulary':
        # TODO: Implement getting scores for vocabulary.
        return {}
    raise ValueError(f"Mode '{mode} is unknown. It needs to be either 'conjugations' or 'vocabulary'.")


def update_scores(root_dir:str, lang:str, user:str, mode:str, scores:list) -> None:
    """
    Updates the scores of a user based on new scores passed to the function given a language and mode.

    ---
    Arguments:
    - root_dir (str): The main directory of the project.
    - lang (str): The language of the quiz where the scores were obtained.
    - user (str): The user whose scores have to be updated.
    - mode (str): The mode of the quiz that produced the scores; either 'conjugations' or 'vocabulary'.

    Returns:
    - None.
    """
    shortened_mode = {'conjugations':'conj', 'vocabulary':'vocab'}[mode]
    with open(os.path.join(root_dir, 'Material', lang, 'users', f"{shortened_mode}scores-{user}.json"), 'w') as scores_file:
        existing_scores = json.load(scores_file)
        if mode == 'conjugations':
            for verb in scores:
                for tense_group in verb:
                    for tense in tense_group:
                        for i in range(len(existing_scores[verb][tense_group][tense])):
                            s = scores[verb][tense_group][tense][i]
                            existing_scores[verb][tense_group][tense][i].append(*s if type(s) == list else s)
        elif mode == 'vocabulary':
            # TODO: Implement updating scores for vocabulary.
            pass