# LangLearn

_Author_: Emili Bonet i Cervera

_Description of the project_:

This project aims to provide a set of scripts that can be used for memorizing certain aspects of the language learning process such as conjugations and vocabulary by quizzing them to the user and evaluating the evolution of the user's proficiency. The data necessary for this is retreived ad-hoc locally depending on the language that the user plans to study. Currently, it is planned to support the following languages:
- French
- German
- Occitan


## Set up

### The Conda environment

Conda is used to set up the environment. In the main directory of this project, there is a YAML file named `langlearn-condaenv.yml` that contains all the dependencies that need to be installed. This environment is created by running the following command:

```
conda env create -f langlearn-condaenv.yml
```

After this installation, activate the `langlearn` environment with the command

```
conda activate langlearn
```

and finally test that it works by running the example code in the next section.

### Downloading material and creating the user record

The `setup.py` script deals with the addition of vocabulary and conjugations for all supported languages, as well as optional users to keep track of one's own progress. To do so, use the following flags:
- `--lang`: Select language to be set up. If None, all supported languages will be referenced.
- `--force`: Ignores existing material, creating the data from scratch.
- `--mode`:
    - 'verbs' will collect verbal material for the language specified;
    - 'addword' will add this word into the vocabulary corpus for the language specified;
    - 'adduser' will create a scores json for the user specified.
- `--username`: Creates a score record for a username indicated in this argument.
- `--newword`: Adds the passed word to the vocabulary corpus.


## Quizzing

The `main.py` script allows to start a new quizzing session. To define it, use the following flags:
- `--lang`: Select language to be practiced.
- `--mode`: Determines what the quiz will be about.
- `--save`: Record results from this quiz.
- `--user`: User where the records will be saved.
- `--word`: Ask this word/verb in particular.
- `--common`: Ask only common words.

When using the flag `--mode conjugations`, a quiz will be started for the verbs of the indicated language in which the user will need to provide the correct conjugations for different tenses and persons, whereas with `--mode vocabulary`, the quiz will be related to the definition and translation of words. Additionally, one can also use the flag `--common` to specify only being asked the most frequent words and verbs in that language, or `-word <YOUR-WORD>` to specify a word/verb in particular.

## Visualization and reporting

(TODO)
