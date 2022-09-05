import numpy as np
import csv
import unicodedata
import re

always_typos = dict()
common_typos = dict()

def fill_typos():

    with open('data/high_valyrian/common_typos.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            common_typos[row[0]] = row[1]

    with open('data/high_valyrian/always_typos.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            always_typos[row[0]] = row[1]

fill_typos()

# sentence translation
# Inputs: (string) answer
#       (boolean) is answer in known language,
#       (int 0-5) skill_level
#       (float) course_percentage
# Outputs: (string) modified answer
#       (float) how many seconds to wait
def human_sentence_translation(answer, known_language, skill_level, course_percentage):

    minimum_feasible_time = 1.6218
    probability_pause = 0.07396

    difficulty =  .85 + .05 * course_percentage + .05 * skill_level

    num_characters = len(answer)
    time_per_letter = 0.1 if known_language else 0.25

    mean1 = time_per_letter * num_characters
    stdev1 = max(0.5, np.random.normal(1, 1))

    mean2 = num_characters * 0.1
    stdev2 = max(0.5, np.random.normal(1, 1))

    d1 = np.random.normal(mean1, stdev1)
    d2 = np.random.normal(mean2, stdev2)

    mean_time = d1 + d2 * (2 - difficulty)

    time_to_answer = get_wait_time(mean_time, minimum_feasible_time, probability_pause, 3)

    answer = add_typos(answer, difficulty)

    return (answer, time_to_answer)

# multiple choice
# Inputs: (int 0-5 skill_level)
#       (float) course_percentage
# Outputs: (boolean) whether you will get it right
#       (float) how many seconds to wait

def human_multiple_choice(skill_level, course_percentage):

    minimum_feasible_time = 0.6218
    probability_pause = 0.0141827

    skill_level = float(skill_level) / 5

    difficulty =  .85 + .05 * course_percentage + .05 * skill_level
    get_correct = np.random.random() < difficulty

    time_to_answer = get_wait_time(2 * difficulty, minimum_feasible_time, probability_pause, 5)

    return (get_correct, time_to_answer)

def get_wait_time(mean_time, minimum_feasible_time, probability_pause, pause_factor):

    minimum_feasible_time = minimum_feasible_time + np.random.random() / 3

    time_to_answer = -1
    while time_to_answer < minimum_feasible_time:

        stdev_time = max(0.5, np.random.normal(1, 1))

        time_to_answer = np.random.normal(mean_time, stdev_time)

    pause = np.random.random() < probability_pause

    if (pause):
        pause_time = pause_factor * mean_time * np.random.random()
        time_to_answer += pause_time

    return time_to_answer

def normalize(str):

    # to lowercase
    str = str.lower()

    # remove accents
    str = ''.join(c for c in unicodedata.normalize('NFD', str)
                   if unicodedata.category(c) != 'Mn')

    # to lowercase
    str = re.sub(r'[^\w\s]','',str)

    return str

def add_typos(str, difficulty):

    str = normalize(str)

    response = ''
    for word in str.split(' '):
        word_with_typos = word

        if (word in always_typos):
            word_with_typos = always_typos[word]
        elif (word in common_typos):
            if (np.random.random() < difficulty / 2):
                word_with_typos = common_typos[word]

        if (np.random.random() < 0.018):
            word_with_typos = word[1:]

        if len(word_with_typos) > 8:

            if 'll' in word_with_typos and np.random.random() < 0.1733:
                string.replace('ll', 'l')

            if 'ie' in word_with_typos and np.random.random() < 0.3653:
                string.replace('ie', 'ei')

            if 'ei' in word_with_typos and np.random.random() < 0.0354:
                string.replace('ei', 'ie')

            if 'ae' in word_with_typos and np.random.random() < 0.2435:
                string.replace('ae', 'ea')

        response += word_with_typos + ' '

    # remove the last space
    response = response[:-1]

    probability_remove_last_char = 0.034
    if np.random.random() < probability_remove_last_char:
        response = response[:-1]

    return response

if __name__ == '__main__':

    print(human_sentence_translation('Daenerys is a strong woman.', True, 1, 0.3))
    print(human_sentence_translation('The leader is blessing the birds.', True, 1, 0.3))
    print(human_sentence_translation('Ābri zaldrīzī ēzi.', True, 1, 0.3))
    print(human_sentence_translation('The knights have commanders.', True, 1, 0.3))
    print(human_sentence_translation('Are they chaining the knights?', True, 1, 0.3))

    print(human_multiple_choice(4, 0.2))
    print(human_multiple_choice(4, 0.2))
    print(human_multiple_choice(4, 0.2))
    print(human_multiple_choice(4, 0.2))
    print(human_multiple_choice(4, 0.2))
