import time
import csv
from process import humanizer
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

class Account (object):
    def __init__ (self, username, password):
        self.username = username
        self.password = password

class DataStorage (object):
    def __init__ (self, new_language, primary_language="english"):
        self.sentence_dictionary = dict()
        self.sentence_dictionary[primary_language] = dict()
        self.sentence_dictionary[new_language] = dict()

        with open(new_language + '/answers_sentences.csv', 'r') as answers_file:
            reader = csv.reader(answers_file)
            for row in reader:
                self.sentence_dictionary[primary_language][row[0]] = row[1]
                self.sentence_dictionary[new_language][row[0]] = row[1]

        with open(new_language + '/answers_other.csv', 'r') as answers_file:
            reader = csv.reader(answers_file)
            for row in reader:
                self.other_dictionary[row[0]] = row[1:]

    def add_sentence(self, sentence, translation, origin_language):
        a, b = self.primary_language, self.new_language
        if origin_language != a:
            a, b = b, a
        self.sentence_dictionary[a][sentence] = translation
        self.sentence_dictionary[b][translation] = sentence

    def add_other(self, prompt, answer):
        self.other_dictionary[prompt].append(answer)

    def write_sentences(self):
        with open(self.new_language + '/answers_sentences.csv', 'w') as answers_file:
            writer = csv.writer(answers_file)
            writer.writerows(self.sentence_dictionary[self.primary_language].items())

    def write_other(self):
        with open(self.new_language + '/answers_other.csv', 'w') as answers_file:
            writer = csv.writer(answers_file)
            for key, answers in self.other_dictionary.items():
                writer.writerow([key] + answers)


class Duolingo (object):
    def __init__ (self):
        self.browser = webdriver.Safari()
        self.browser.maximize_window()
        self.gold_class = '_3dqWQ'
        self.dictionary = dict()

        with open('high_valyrian/answers.csv', 'r') as answers_file:
            reader = csv.reader(answers_file)
            for row in reader:
                self.dictionary[row[0]] = row[1]

        with open('high_valyrian/current_skill.txt', 'r') as current_skill_file:
            file_content = current_skill_file.readline().strip()
            if file_content != '':
                self.current_skill = int(file_content)
            else:
                self.current_skill = 0

    def log_in(self, account):

        have_account = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="have-account"]'))
        )

        have_account.click()

        email_field = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@data-test="email-input"]'))
        )

        time.sleep(1)

        email_field.send_keys(account.username)

        password_field = self.browser.find_element(By.XPATH,
                                             '//input[@data-test="password-input"]')
        password_field.send_keys(account.password)

        login_button = self.browser.find_element(By.XPATH,
                                           '//button[@data-test="register-button"]')
        login_button.click()

    def skip (self):
        skip = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//button[@data-test="player-skip"]')))
        skip.click()

    def go_next(self):
        next_button = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//button[@data-test="player-next"]')))
        next_button.click()

    def use_keyboard (self):
        try:
            button = WebDriverWait(self.browser, .2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@data-test="player-toggle-keyboard"]'))
            )

            if button.text == "Use keyboard" or button.text == "Make harder":
                button.click()
        except WebDriverException:
            pass

    def alt_solution_check(self, solution):
        return len(solution) > 17 and solution[0:17] == "Correct solution:"

    def is_on_homepage(self):
        try:
            self.browser.find_element(By.XPATH, '//div[@data-test="home"]')
            return True
        except WebDriverException:
            return False

    def start_intro(self):
        intro = WebDriverWait(session.browser, 4).until(EC.presence_of_element_located((By.XPATH, '//a[@data-test="intro-lesson"]')))

        intro.click()

        session.complete_skill(0, 1)

    def is_near_finished(self, skill):
        try:
            level_text = skill.find_element(By.CSS_SELECTOR, 'div._1m77f').text
            print(level_text)
            fraction_1 = level_text.split(' ')[1]
            fraction_1_array = fraction_1.split('/')
            is_on_last_lesson = (fraction_1_array[0] == '5' and fraction_1_array[1] == '6') or  (fraction_1_array[0] == fraction_1_array[1])

            lesson_text = skill.find_element(By.CSS_SELECTOR, 'div.RXDIm').text
            fraction_2 = lesson_text.split(' ')[1]
            fraction_2_array = fraction_2.split('/')
            is_on_last_level = int(fraction_2_array[1]) == int(fraction_2[0]) + 1

            return is_on_last_level and is_on_last_lesson
        except WebDriverException:
            return False


    def is_finished(self, skill):
        try:
            skill.find_element(By.CLASS_NAME, self.gold_class)
            return True
        except WebDriverException:
            return False

    def skill_level(self, skill):
        try:
            lvl = skill.find_element(By.CSS_SELECTOR, 'div[data-test="level crown"]').text
            return int(lvl)
        except:
            return 0

    def start_button(self, skill):
        try:
            skill.find_element(By.CSS_SELECTOR, 'div[data-test="skill-popout"]')
        except WebDriverException:
            toggle_dropdown = skill.find_element(By.CSS_SELECTOR, 'div._2eeKH')
            toggle_dropdown.send_keys(Keys.RETURN)
            time.sleep(.1)

        start_skill = skill.find_element(By.CSS_SELECTOR, 'a[data-test="start-button"]')
        return start_skill

    def find_xp_gain(self, start_button):
        return int(start_button.text.split(' ')[1])

    def save(self):
        print("Closing files")

        with open('high_valyrian/answers.csv', 'w') as answers_file:
            writer = csv.writer(answers_file)
            writer.writerows(self.dictionary.items())

        with open('high_valyrian/current_skill.txt', 'w') as current_skill_file:
            current_skill_file.write(str(self.current_skill))

    def challenge_translate(self, skill_level, course_percentage):

        sentence = self.browser.find_element(By.XPATH, '//div[@class="_1KUxv _11rtD"]').text
        sentence += " (t)"

        if sentence in self.dictionary:
            self.use_keyboard()

            input_field = self.browser.find_element(By.XPATH,
                                              '//textarea[@data-test="challenge-translate-input"]')

            answer = self.dictionary[sentence]
            processed_answer, wait_time = humanizer(answer, skill_level, course_percentage, 'translate')
            time.sleep(wait_time)
            input_field.send_keys(processed_answer)
            input_field.send_keys(Keys.RETURN)

        else:
            self.skip()

            solution = self.browser.find_element(By.XPATH,
                                           '//div[@class="_1UqAr _3Qruy"]').text

            if (self.alt_solution_check(solution)):
                solution = solution[17:]

            self.dictionary[sentence] = solution

        self.go_next()

    def challenge_select(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH,
                                       '//h1[@data-test="challenge-header"]').text
        sentence += " (s)"
        if sentence in self.dictionary:
            choices = self.browser.find_elements(By.XPATH, '//span[@class="HaQTI"]')

            for choice in choices:
                if choice.text == self.dictionary[sentence]:
                    choice.click()

        else:
            self.skip()

            solution = self.browser.find_element(By.XPATH,
                                           '//div[@class="_1UqAr _3Qruy"]').text

            self.dictionary[sentence] = solution

        self.go_next()

    def challenge_form(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH,
                                       '//div[@class="_2SfAl _2Hg6H"]').get_attribute('data-prompt')
        sentence += " (f)"
        print(sentence)
        if sentence in self.dictionary:
            choices = self.browser.find_elements(By.XPATH,
                                           '//div[@data-test="challenge-judge-text"]')
            for choice in choices:
                if choice.text == self.dictionary[sentence]:
                    choice.click()
        else:
            print('boop')
            self.skip()
            solution = self.browser.find_element(By.XPATH,
                                           '//div[@class="_1UqAr _3Qruy"]')
            self.dictionary[sentence] = solution.text

        self.go_next()

    def challenge_name(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH,
                                       '//h1[@data-test="challenge-header"]').text
        sentence += " (n)"
        if sentence in self.dictionary:
            input_field = self.browser.find_element(By.XPATH,
                                              '//input[@data-test="challenge-text-input"]')
            input_field.send_keys(self.dictionary[sentence])
            input_field.send_keys(Keys.RETURN)
            time.sleep(.3)

        else:
            self.skip()

            solution = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_1UqAr _3Qruy"]'))).text

            self.dictionary[sentence] = solution

        self.go_next()

    def challenge_complete_reverse_translation(self, skill_level, skill_no):
        input_field = self.browser.find_element(By.XPATH, '//input[@data-test="challenge-text-input"]')
        answer = self.browser.find_element(By.XPATH, '//div[@class="caPDQ"]').text
        input_field.send_keys(answer)
        input_field.send_keys(Keys.RETURN)
        time.sleep(.35)

    def challenge_partial_reverse_translate(self, skill_level, skill_no):
        input_field = self.browser.find_element(By.XPATH, '//span[@spellcheck="False"]')
        answer = self.browser.find_element(By.XPATH, '//span[@class="_1yM6s _1vqO5"]').text
        input_field.send_keys(answer)
        input_field.send_keys(Keys.RETURN)
        time.sleep(.35)

    def complete_skill(self, level, course_percentage):

        skill_completed = False

        while not skill_completed:
            while True:
                try:
                    challenge = session.browser.find_element(By.XPATH,
                                                    '//div[@data-test="challenge challenge-translate"]')
                    print("translate time", time.time())

                    self.challenge_translate(level, course_percentage)
                    continue
                except WebDriverException as e:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH,
                                                    '//div[@data-test="challenge challenge-select"]')
                    print("selection time", time.time())
                    self.challenge_select(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH,
                                                    '//div[@data-test="challenge challenge-form"]')
                    time.sleep(.3)
                    print("form time", time.time())
                    self.challenge_form(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    try:
                        challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-name"]')
                    except:
                        challenge = self.browser.find_element(By.XPATH, '//div[@data-test="ge challenge-name"]')

                    print("naming time", time.time())
                    self.challenge_name(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-completeReverseTranslation"]')
                    self.challenge_complete_reverse_translation(level, course_percentage)
                    continue
                except:
                    pass

                try:
                    self.go_next()
                    continue
                except WebDriverException:
                    pass

                try:
                    if self.is_on_homepage():
                        skill_completed = True
                        break
                except:
                    continue

                try:
                    print("no thanks 1", time.time())
                    no_thanks = self.browser.find_element(By.XPATH, '//button[@data-test="plus-no-thanks"]')
                    no_thanks.click()
                except WebDriverException:
                    pass

                try:
                    print("no thanks 2", time.time())
                    no_thanks_2 = self.browser.find_element(By.XPATH, '//button[@class="WOZnx _275sd _1ZefG _47xRj U1P3s _40EaN"]')
                    no_thanks_2.click()
                except WebDriverException:
                    pass

                try:
                    print("maybe later", time.time())
                    maybe_later = self.browser.find_element(By.XPATH, '//button[@data-test="maybe-later"]')
                    maybe_later.click()
                except WebDriverException:
                    pass

                try:
                    print("Piss off", time.time())
                    piss_off = self.browser.find_element(By.XPATH, '//button[@data-test="plus-close-x"]')
                    piss_off.click()
                except WebDriverException:
                    pass

                try:
                    start_preview = self.browser.find_element(By.XPATH, '//button[@class="_3HhhB _2NolF _275sd _1ZefG _3bnKZ _1Rcu8 _3PMUi"]')
                    if button.text == 'Start my free preview':
                        button.click()
                except WebDriverException:
                    pass

            time.sleep(5)

    def learn_bot(self):
        while True:

            skills = WebDriverWait(self.browser, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-test="skill"]')))
            num_skills = len(skills)

            # Scroll to appoximate location of the skill in order for its information to fully load
            course_percentage = self.current_skill / num_skills
            scroll = "window.scrollTo(0, document.body.scrollHeight * " + str(course_percentage) + ");"
            self.browser.execute_script(scroll)

            skill = skills[self.current_skill]

            skill_level = self.skill_level(skill)

            try:
                start_button = self.start_button(skill)
            except WebDriverException:
                self.browser.execute_script(scroll)
                start_button = self.start_button(skill)

            xp = self.find_xp_gain(start_button)

            if xp <= 0:
                break

            increment = self.is_finished(skill) or self.is_near_finished(skill)

            start_button.click()
            self.complete_skill(skill_level, course_percentage)

            if increment:
                self.current_skill = (self.current_skill + 1) % num_skills


session = Duolingo()

def main(session):
    me = Account('odeeogbfrpysdkgxbj@bvhrs.com', 'PZrmkxbamu3eUA9')
    #me = Account('stuff0009@gmail.com', 'duolingodotcom')

    session.browser.get("https://www.duolingo.com/learn")

    session.log_in(me)

    while not session.is_on_homepage():
        time.sleep(2)

    try:
        session.start_intro()
    except WebDriverException:
        pass

    session.learn_bot()

    session.save()

try:
    main(session)
except KeyboardInterrupt:
    session.save()
