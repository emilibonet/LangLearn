import os
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager


def instantiate_driver() -> Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # it's more scalable to work in headless mode 
    chrome_path = ChromeDriverManager().install() 
    chrome_service = Service(chrome_path)
    return Chrome(options=options, service=chrome_service)


class ConjugationCollector():
    """
    Used to collect the conjugations of a given language.
    """
    def __init__(self, root_dir):
        """
        Initializes the ConjugationCollector object.

        Arguments:
            - root_dir (str): The root directory of the project.

        Returns
            - A ConjugationCollector instance.
        """
        self.parsers = {
        'french': self.fr_conjugation_parser,
        'german': self.ge_conjugation_parser,
        'occitan': self.oc_conjugation_parser
        }
        self.websites = {
        'french': lambda infinitive: f'https://www.verbix.com/webverbix/go.php?D1=3&T1={infinitive}',
        'german': lambda infinitive: ...,
        'occitan': lambda infinitive: ...
        }
        self.root = root_dir
    
    @staticmethod
    def fr_conjugation_parser(driver:Chrome, infinitive:str=None, group:str=None) -> tuple:
        """
        Extracts the conjugation from the raw list; capable of parsing the Verbix conjugation pages for French
        (e.g. www.verbix.com/webverbix/go.php?D1=3&T1=avoir).

        Arguments:
            - raw (list): A list with the extracted lines from the conjugation webpage.
            - infinitive (str): The infinitive of the verb.
            - group (str): The group of the verb.

        Returns:
            - A tuple consisting of a dictionary with the conjugation of the given verb and another dictionary with the structure for the score data.
        """
        raw = [x.text.split('\n') for x in driver.find_elements(By.CLASS_NAME, "columns-main")][0]  # Will throw an exception if the infinitive was not found.
        curr_1st_tier_keyword = curr_2nd_tier_keyword = ''
        keywords_1st_tier = ['Indicatif', 'Subjonctif', 'Conditionnel', 'Imperatif', 'Translations']
        keywords_2nd_tier = ['Présent', 'Passé composé', 'Imparfait', 'Plus-que-parfait', 'Futur simple', 'Futur antérieur',
                            'Passé simple', 'Passé antérieur', 'Passé composé', 'Plus-que-parfait', 'Passé']
        conjugation = [raw[1].split(' ')[1] if infinitive is None else infinitive,
                        {'Nominal Forms':
                        {'Infinitif': [raw[1].split(' ')[1]],
                            'Gérondif': raw[2].split(' ')[-2:],
                            'Participe': raw[3].split(' ')[-2:]}}]
        empty_scores = [raw[1].split(' ')[1],
                {'Nominal Forms':
                {'Infinitif': [[]],
                    'Gérondif': [[]],
                    'Participe': [[]]}}]
        try:
            skip_similar_conjugations = is_translation = False
            for line in raw[6:]:
                if line == 'Synonyms & Antonyms':  # Not interested in the rest of the page.
                    break
                if 'Verbs' in line or skip_similar_conjugations:
                    # It arrived at the end.
                    skip_similar_conjugations = not skip_similar_conjugations
                    continue
                if line in keywords_1st_tier:
                    curr_1st_tier_keyword = line
                    conjugation[1][curr_1st_tier_keyword] = {}
                    empty_scores[1][curr_1st_tier_keyword] = {}
                    if curr_1st_tier_keyword in ['Imperatif', 'Translations']:
                        is_translation = curr_1st_tier_keyword == 'Translations'
                        curr_2nd_tier_keyword = curr_1st_tier_keyword
                        conjugation[1][curr_1st_tier_keyword][curr_2nd_tier_keyword] = []
                        empty_scores[1][curr_1st_tier_keyword][curr_2nd_tier_keyword] = []
                elif line in keywords_2nd_tier:
                    curr_2nd_tier_keyword = line
                    conjugation[1][curr_1st_tier_keyword][curr_2nd_tier_keyword] = []
                    empty_scores[1][curr_1st_tier_keyword][curr_2nd_tier_keyword] = []
                else:
                    splitline = line.split(' ')
                    if is_translation:
                        conjugation[1][curr_1st_tier_keyword][curr_2nd_tier_keyword].append(' '.join(splitline))
                        continue  # No scores for translation.
                    if '/' in line:  # Has pronounciation.
                        conjugation[1][curr_1st_tier_keyword][curr_2nd_tier_keyword].append([splitline[0], ' '.join(splitline[1:-1]), splitline[-1]])
                    else:  # No pronounciation.
                        conjugation[1][curr_1st_tier_keyword][curr_2nd_tier_keyword].append([splitline[0], ' '.join(splitline[1:]), '<NA>'])
                    empty_scores[1][curr_1st_tier_keyword][curr_2nd_tier_keyword].append([])
            return conjugation, empty_scores
        except:
            print(f"ERROR - Status: Current line is '{line}'; Keyword hierarchy: {curr_1st_tier_keyword} > {curr_2nd_tier_keyword}")

    @staticmethod
    def ge_conjugation_parser(driver:Chrome, infinitive:str=None, group:str=None) -> tuple:
        pass

    @staticmethod
    def oc_conjugation_parser(driver:Chrome, infinitive:str=None, group:str=None) -> tuple:
        pass


    def _configure_crawl(self, language:str, force:bool) -> tuple:
        """
        Instantiates the parser, infinitive list and the selenium webdriver.

        ---
        Arguments:
        - language (str): The language to crawl.
        - force (bool): Whether to force the remake the database from scratch.

        Returns:
        - tuple: the existing conjugation, the empty scores, the parser and the infinitive list.
        """
        with open(os.path.join(self.root, 'Material', language, '.infinitives-complete.json'), 'r') as infinitives_file:
            infinitives = json.load(infinitives_file)
        if force:
            return [{}, {}, self.parsers[language], infinitives, instantiate_driver()]
        
        with open(os.path.join(self.root, 'Material', language, 'conjugations.json'), 'r') as conjugation_file:
            conjugations = json.load(conjugation_file)
        with open(os.path.join(self.root, 'Material', language, '.conjscores-template.json'), 'r') as scores_file:
            scores = json.load(scores_file)
        return (conjugations, scores, self.parsers[language], infinitives, instantiate_driver())


    def collect(self, language:str, force:bool=False) -> tuple:
        """
        Crawls the conjugations webpage of the given language.

        Arguments:
            - language (str): The language to crawl.
            - force (bool): Whether to force the remake of the database from scratch.

        Returns:
            - tuple: the updated conjugation, the empty scores, and the uncatched verbs.
        """
        if language not in self.parsers.keys():
            raise ValueError(f"Language '{language}' not supported.")
        conjugations, scores, conjugation_parser, infinitives, driver = self._configure_crawl(language, force)
        uncatched_verbs = []

        try:
            print(f"Starting conjugation crawl for '{language}'.")
            is_dict = True
            if type(infinitives) is not dict:
                is_dict = False
                infinitives = {'No Group': infinitives}
            for group in infinitives:
                print(f"Processing group '{group}'.") if is_dict else None
                for infinitive in tqdm(infinitives[group]):
                    if infinitive in conjugations.keys():
                        continue   # Do not remake.
                    try:
                        driver.get(self.websites[language](infinitive))
                        conj, empty_scores = conjugation_parser(driver, infinitive, group)
                        conjugations[conj[0]] = conj[1]
                        scores[empty_scores[0]] = empty_scores[1]
                    except:  # Infinitive was not found in the conjugations webpage.
                        uncatched_verbs.append(infinitive)
        except Exception as err:
            print(f"ERROR - Crawl stopped: {err}")
        finally:
            driver.close()
        return (conjugations, scores, uncatched_verbs)


class VocabularyCollector():
    def __init__(self, root_dir:str=os.path.dirname(os.path.realpath(__file__))):
        self.root = root_dir

        self.parsers = {
            'french': self.fr_vocabulary_parser,
            'german': self.ge_vocabulary_parser,
            'occitan': self.oc_vocabulary_parser
        }
        self.websites = {
            'french': lambda word: f"https://www.larousse.fr/dictionnaires/francais/{word}/",
            'german': lambda word: ...,
            'occitan': lambda word: ...
        }

    @staticmethod
    def fr_vocabulary_parser(driver:Chrome, word:str) -> tuple:
        raw = [x.text.split('\n') for x in driver.find_elements(By.CLASS_NAME, "DivisionDefinition")]
        if len(raw) == 0:
            raise Exception(f"Word '{word}' was not found.")
        # TODO: Finish empty_scores.
        out, empty_scores, is_digit = [word, []], [word, []], lambda x: ord('0') <= ord(x) and ord(x) <= ord('9')
        for acceptation in raw:
            definition_index = int(not is_digit(acceptation[0][0]) and not '.' in acceptation[0])  # If there's a title, skip it.
            skip_num = 3 if is_digit(acceptation[definition_index][0]) else 0  # If there's a number, skip it to get only the definition.
            out[1].append({"Definition": acceptation[definition_index][skip_num:], "Synonyms" : [], "Antonyms": [], 'Translations': []})
            for idx, line in enumerate(acceptation[1:]):
                if "Synonymes" in line or "Antonymes" in line:  # Next line contains synonyms or antonyms.
                    out[1][-1][line.replace('e', '').strip(" :")].append(acceptation[idx+2].split(" - "))
        return (out, empty_scores)
    
    @staticmethod
    def ge_vocabulary_parser(driver:Chrome, word:str) -> tuple:
        ...
    
    @staticmethod
    def oc_vocabulary_parser(driver:Chrome, word:str) -> tuple:
        ...

    def _configure_lookup(self, language:str) -> tuple:
        """
        Instantiates the parser and the selenium webdriver, and recovers the existing vocabulary and the scores template.

        ---
        Arguments:
        - language (str): The language to lookup.

        Return:
        - tuple: consisting of the vocabulary, the scores template, the parser,
        """        
        with open(os.path.join(self.root, 'Material', language, 'vocabulary.json'), 'r') as vocabulary_file:
            vocabulary = json.load(vocabulary_file)
        with open(os.path.join(self.root, 'Material', language, '.vocabscores-template.json'), 'r') as scores_file:
            scores = json.load(scores_file)
        return (vocabulary, scores, self.parsers[language], instantiate_driver())


    def collect(self, word, language:str, force:bool=False):
        if language not in self.parsers.keys():
            raise ValueError(f"Language '{language}' not supported.")
        vocabulary, scores, vocabulary_parser, driver = self._configure_lookup(language)
        try:
            if not force and word in vocabulary.keys():
                raise ValueError(f"Word '{word}' already in the vocabulary.")
            driver.get(self.websites[language](word))
            vocab, empty_scores = vocabulary_parser(driver, word)
            vocabulary[vocab[0]] = vocab[1]
            scores[empty_scores[0]] = empty_scores[1]
        except Exception as err:
            raise Exception(f"ERROR - Lookup stopped: {err}")
        finally:
            driver.close()
        return (vocabulary, scores)

