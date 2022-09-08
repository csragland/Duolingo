import csv

class DataStorage (object):
    def __init__ (self, learning_language, known_language="english"):
        self.LEARNING_LANGUAGE = learning_language
        self.KNOWN_LANGUAGE = known_language

        self.sentence_dictionary = dict()
        self.sentence_dictionary[known_language] = dict()
        self.sentence_dictionary[learning_language] = dict()
        self.other_dictionary = dict()

        with open('data/' + learning_language + '/answers_sentences.csv', 'r') as answers_file:
            reader = csv.reader(answers_file)
            for row in reader:
                self.sentence_dictionary[known_language][row[0]] = row[1]
                self.sentence_dictionary[learning_language][row[1]] = row[0]

        with open('data/' + learning_language + '/answers_other.csv', 'r') as answers_file:
            reader = csv.reader(answers_file)
            for row in reader:
                self.other_dictionary[row[0]] = row[1:]

        with open('data/' + learning_language + '/current_skill.txt', 'r') as current_skill_file:
            file_content = current_skill_file.readline().strip()
            if file_content != '':
                self.current_skill = int(file_content)
            else:
                self.current_skill = 0

    def add_sentence(self, sentence, translation, sentence_language):
        a, b = self.KNOWN_LANGUAGE, self.LEARNING_LANGUAGE
        if sentence_language != a:
            a, b = b, a
        self.sentence_dictionary[a][sentence] = translation
        self.sentence_dictionary[b][translation] = sentence

    def add_other(self, prompt, answer):
        if not prompt in self.other_dictionary:
            self.other_dictionary[prompt] = [answer]
        else:
            self.other_dictionary[prompt].append(answer)

    def update_current_skill(self, new):
        self.current_skill = new

    def write_sentences(self):
        with open('data/' + self.LEARNING_LANGUAGE + '/answers_sentences.csv', 'w') as answers_file:
            writer = csv.writer(answers_file)
            writer.writerows(self.sentence_dictionary[self.KNOWN_LANGUAGE].items())

    def write_other(self):
        with open('data/' + self.LEARNING_LANGUAGE + '/answers_other.csv', 'w') as answers_file:
            writer = csv.writer(answers_file)
            for key, answers in self.other_dictionary.items():
                writer.writerow([key] + answers)

    def write_current_skill(self):
        with open('data/' + self.LEARNING_LANGUAGE + '/current_skill.txt', 'w') as current_skill_file:
            current_skill_file.write(str(self.current_skill))
