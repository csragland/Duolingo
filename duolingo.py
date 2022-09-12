import time
import random

import humanize
from data_storage import DataStorage

from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

class Duolingo (object):
    def __init__(
            self,
            learning_language,
            known_language='english',
            covert=False,
            humanize=False):
        if covert:
            self.browser = uc.Chrome()
        else:
            self.browser = webdriver.Safari()
        self.data = DataStorage(learning_language)

        self.LEARNING_LANGUAGE = learning_language
        self.KNOWN_LANGUAGE = known_language
        self.HUMANIZE = humanize
        self.WRONG_CUTOFF = 3

        self.browser.maximize_window()

    def log_in(self, username, password):

        have_account = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="have-account"]'))
        )

        self.click(have_account)

        email_field = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@data-test="email-input"]'))
        )

        time.sleep(1)

        email_field.send_keys(username)

        password_field = self.browser.find_element(
            By.XPATH, '//input[@data-test="password-input"]')
        password_field.send_keys(password)

        login_button = self.browser.find_element(
            By.XPATH, '//button[@data-test="register-button"]')
        self.click(login_button)

    def skip(self):
        skip = WebDriverWait(
            self.browser, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="player-skip"]')))
        print("SKIPPING")
        self.click(skip, 'skip')

    def go_next(self, special=False):
        next_button = WebDriverWait(
            self.browser, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="player-next"]')))
        if next_button.text == "Learn more":
            raise WebDriverException('This is a fake next button')
        if not special:
            self.click(next_button, 'next')
        else:
            self.click(next_button, 'next')
            self.click(next_button, 'next')

    def use_keyboard(self):
        try:
            button = WebDriverWait(
                self.browser, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@data-test="player-toggle-keyboard"]')))

            text = button.text.strip().lower()
            if text == "use keyboard" or text == "make harder":
                self.click(button)
        except WebDriverException:
            pass

    def alt_solution_check(self, solution):
        return len(solution) > 17 and solution[0:17] == "Correct solution:"

    def reformat(self, sentence):
        a = sentence.replace('  ', ' ')
        b = a.replace(' ?', '?')
        c = b.replace(' .', '.')
        d = c.replace(' !', '!')
        return d

    def is_on_homepage(self):
        try:
            self.browser.find_element(By.XPATH, '//div[@data-test="home"]')
            return True
        except WebDriverException:
            return False

    def start_intro(self):
        intro = WebDriverWait(
            self.browser, 4).until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[@data-test="intro-lesson"]')))

        self.click(intro)

        self.complete_skill(0, 1)

    def will_be_finished(self, skill):
        try:
            level_text = skill.find_element(By.CSS_SELECTOR, 'div._1m77f').text.strip().lower()
            if level_text == 'legendary level':
                return True

            # Level 4/6
            fraction_1 = level_text.split(' ')[1]
            fraction_1_array = fraction_1.split('/')
            is_on_last_level = int(
                fraction_1_array[0]) + 2 == int(fraction_1_array[1])

            # Lesson 4/5
            lesson_text = skill.find_element(By.CSS_SELECTOR, 'div.RXDIm').text
            fraction_2 = lesson_text.split(' ')[1]
            fraction_2_array = fraction_2.split('/')
            is_on_last_lesson = int(
                fraction_2_array[0]) + 1 == int(fraction_2_array[1])

            return is_on_last_level and is_on_last_lesson
        except WebDriverException:
            return False

    def skill_level(self, skill):
        try:
            lvl = skill.find_element(
                By.CSS_SELECTOR,
                'div[data-test="level crown"]').text
            return int(lvl)
        except BaseException:
            return 0

    def start_button(self, skill):
        try:
            skill.find_element(
                By.CSS_SELECTOR,
                'div[data-test="skill-popout"]')
        except WebDriverException:
            toggle_dropdown = skill.find_element(By.CSS_SELECTOR, 'div._2eeKH')
            toggle_dropdown.send_keys(Keys.RETURN)
            time.sleep(.1)

        start_skill = skill.find_element(
            By.CSS_SELECTOR, 'a[data-test="start-button"]')
        return start_skill

    def find_xp_gain(self, start_button):
        return int(start_button.text.split(' ')[1])

    def find_prompt_language(self):
        prompt = WebDriverWait(
            self.browser, 1).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1[data-test="challenge-header"]'))).text
        assert prompt[:14] == 'Write this in ', 'Unusual translation prompt: ' + prompt
        language = prompt[14:].replace(' ', '_').lower()
        if language == self.KNOWN_LANGUAGE:
            return self.LEARNING_LANGUAGE
        elif language == self.LEARNING_LANGUAGE:
            return self.KNOWN_LANGUAGE
        else:
            raise Exception('unknown language prompted for translation')

    def get_misc_answer(self, prompt):
        self.skip()
        solution = WebDriverWait(
            self.browser, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="_1UqAr _3Qruy"]'))).text

        self.data.add_other(prompt, solution)

    def save(self):
        print("Closing files")

        self.data.write_sentences()
        self.data.write_other()

        self.data.write_current_skill()

    def click(self, element, element_type=''):
        if self.HUMANIZE:
            if element_type == '':
                time.sleep(humanize.get_wait_time(1.7, .7, .4))
            elif element_type == 'next':
                time.sleep(humanize.get_wait_time(.4, .2, .1))
            elif element_type == 'skip':
                time.sleep(humanize.get_wait_time(5,2, 2.9))
            elif element_type == 'spam':
                time.sleep(humanize.get_wait_time(1.6, .8, .5))
            elif element_type == 'enter':
                time.sleep(humanize.get_wait_time(1.4, .5, .1))
            else:
                time.sleep(humanize.get_wait_time(1.7, .5))
        element.click()

    def submit_translation_answer(self, answer, is_known_language, input_field, skill_level, course_percentage, skip_humanize):
        if not self.HUMANIZE:
            input_field.send_keys(answer)
            input_field.send_keys(Keys.RETURN)
        else:
            processed_answer, wait_time = humanize.human_sentence_translation(
                answer, is_known_language, skill_level, course_percentage)
            if skip_humanize:
                processed_answer = humanize.normalize(answer)
                wait_time += 1.7
            print(processed_answer, wait_time)
            time.sleep(wait_time)
            input_field.send_keys(processed_answer)
            input_field.send_keys(Keys.RETURN)

    def try_submit_mc_answer(self, choices, prompt, skill_level, course_percentage, challenge_type):
        answer = None
        for choice in choices:
            if choice.text in self.data.other_dictionary[prompt]:
                answer = choice
                break
        if answer:
            choose_correctly = True
            if self.HUMANIZE:
                if challenge_type == 'select':
                    choose_correctly = True
                    wait_time = .05
                else:
                    choose_correctly, wait_time = humanize.human_multiple_choice(skill_level, course_percentage)
                time.sleep(wait_time)
            if not choose_correctly:
                print("GUESSING")
                self.click(random.choice(choices), 'enter')
            else:
                self.click(answer, 'enter')
        else:
            self.get_misc_answer(prompt)

    def challenge_translate(
            self,
            skill_level,
            course_percentage,
            wrong_count,
            reverse=False):

        sentence = self.browser.find_element(
            By.XPATH, '//div[@class="_1KUxv _11rtD"]').text

        sentence = self.reformat(sentence)

        if not sentence in wrong_count:
            wrong_count[sentence] = 0
        else:
            wrong_count[sentence] += 1
        skip_humanize = wrong_count[sentence] >= self.WRONG_CUTOFF
        replace_answer = wrong_count[sentence] >= self.WRONG_CUTOFF + 1

        if not reverse:
            WebDriverWait(
                self.browser, 2).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[@data-test="challenge challenge-translate"]')))
            prompt_language = self.find_prompt_language()
            is_known_language = prompt_language == self.LEARNING_LANGUAGE
        else:
            prompt_language = self.KNOWN_LANGUAGE
            is_known_language = False

        if sentence in self.data.sentence_dictionary[prompt_language] and not replace_answer:

            try:
                input_field = self.browser.find_element(
                    By.XPATH, '//textarea[@data-test="challenge-translate-input"]')
            except WebDriverException:
                self.use_keyboard()
                input_field = self.browser.find_element(
                    By.XPATH, '//textarea[@data-test="challenge-translate-input"]')

            answer = self.data.sentence_dictionary[prompt_language][sentence]

            self.submit_translation_answer(answer, is_known_language, input_field, skill_level, course_percentage, skip_humanize)

        else:
            self.skip()

            solution = self.browser.find_element(
                By.XPATH, '//div[@class="_1UqAr _3Qruy"]').text

            if (self.alt_solution_check(solution)):
                solution = solution[17:]

            solution = self.reformat(solution)

            self.data.add_sentence(sentence, solution, prompt_language)

            if replace_answer:
                wrong_count[sentence] = 0

        self.go_next()

    def challenge_select(self, skill_level, course_percentage):
        prompt = self.browser.find_element(
            By.XPATH, '//h1[@data-test="challenge-header"]').text
        prompt += " (s)"

        if prompt in self.data.other_dictionary:
            choices = self.browser.find_elements(
                By.XPATH, '//span[@class="HaQTI"]')

            self.try_submit_mc_answer(choices, prompt, skill_level, course_percentage, 'select')

        else:
            self.get_misc_answer(prompt)

        self.go_next(self.HUMANIZE)

    def challenge_form(self, skill_level, course_percentage):
        prompt = self.browser.find_element(
            By.XPATH, '//div[@class="_2SfAl _2Hg6H"]').get_attribute('data-prompt')
        prompt += " (f)"

        if prompt in self.data.other_dictionary:
            choices = self.browser.find_elements(
                By.XPATH, '//div[@data-test="challenge-judge-text"]')

            self.try_submit_mc_answer(choices, prompt, skill_level, course_percentage, 'form')

        else:
            self.get_misc_answer(prompt)

        self.go_next(self.HUMANIZE)

    def challenge_name(self, skill_level, course_percentage, wrong_count):
        prompt = self.browser.find_element(
            By.XPATH, '//h1[@data-test="challenge-header"]').text
        prompt += " (n)"

        if not prompt in wrong_count:
            wrong_count[prompt] = 0
        else:
            wrong_count[prompt] += 1
        skip_humanize = wrong_count[prompt] >= self.WRONG_CUTOFF
        replace_answer = wrong_count[prompt] >= self.WRONG_CUTOFF + 1

        if prompt in self.data.other_dictionary and not replace_answer:
            answer = self.data.other_dictionary[prompt][0]
            input_field = self.browser.find_element(
                By.XPATH, '//input[@data-test="challenge-text-input"]')

            self.submit_translation_answer(answer, False, input_field, skill_level, course_percentage, skip_humanize)

        else:
            self.get_misc_answer(prompt)

            if replace_answer:
                wrong_count[prompt] = 0

        self.go_next()

    def challenge_partial_reverse_translate(self, skill_level, skill_no):
        input_field = self.browser.find_element(
            By.XPATH, '//span[@spellcheck="False"]')
        answer = self.browser.find_element(
            By.XPATH, '//span[@class="_1yM6s _1vqO5"]').text
        input_field.send_keys(answer)
        input_field.send_keys(Keys.RETURN)

    def complete_skill(self, level, course_percentage):

        skill_completed = False
        wrong_count = dict()

        while not skill_completed:
            while True:
                time.sleep(.4)
                try:
                    self.browser.find_element(
                        By.XPATH, '//div[@data-test="challenge challenge-translate"]')

                    self.challenge_translate(level, course_percentage, wrong_count)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(
                        By.XPATH, '//div[@data-test="challenge challenge-select"]')
                    self.challenge_select(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(
                        By.XPATH, '//div[@data-test="challenge challenge-form"]')
                    self.challenge_form(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    try:
                        challenge = self.browser.find_element(
                            By.XPATH, '//div[@data-test="challenge challenge-name"]')
                    except BaseException:
                        challenge = self.browser.find_element(
                            By.XPATH, '//div[@data-test="ge challenge-name"]')

                    self.challenge_name(level, course_percentage, wrong_count)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(
                        By.XPATH, '//div[@data-test="challenge challenge-completeReverseTranslation"]')
                    self.challenge_translate(level, course_percentage, wrong_count, True)
                    continue
                except WebDriverException:
                    pass

                try:
                    self.go_next()
                    continue
                except WebDriverException:
                    pass

                try:
                    no_thanks = self.browser.find_element(
                        By.XPATH, '//button[@data-test="plus-no-thanks"]')
                    self.click(no_thanks, 'spam')
                except WebDriverException:
                    pass

                try:
                    no_thanks_2 = self.browser.find_element(
                        By.XPATH, '//button[@class="WOZnx _275sd _1ZefG _47xRj U1P3s _40EaN"]')
                    self.click(no_thanks_2, 'spam')
                except WebDriverException:
                    pass

                try:
                    maybe_later = self.browser.find_element(
                        By.XPATH, '//button[@data-test="maybe-later"]')
                    self.click(maybe_later, 'spam')
                except WebDriverException:
                    pass

                try:
                    piss_off = self.browser.find_element(
                        By.XPATH, '//button[@data-test="plus-close-x"]')
                    self.click(piss_off, 'spam')
                except WebDriverException:
                    pass

                try:
                    start_preview = self.browser.find_element(
                        By.XPATH, '//button[@class="_3HhhB _2NolF _275sd _1ZefG _3bnKZ _1Rcu8 _3PMUi"]')
                    if start_preview.text == 'Start my free preview':
                        self.click(start_preview, 'spam')
                except WebDriverException:
                    pass

                if self.is_on_homepage():
                    skill_completed = True
                    break

            time.sleep(4)
            try:
                ad1 = self.browser.find_element(
                    By.XPATH, '//button[@data-test="notification-drawer-no-thanks-button"]')
                self.click(ad1, 'spam')
            except BaseException:
                pass
            try:
                ad2 = self.browser.find_element(
                    By.XPATH, '//div[@data-test="close-button"]')
                self.click(ad2, 'spam')
            except BaseException:
                pass
            time.sleep(.5)

    def do_next_skill(self):
        skills = WebDriverWait(
            self.browser, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div[data-test="skill"]')))
        num_skills = len(skills)

        # Scroll to appoximate location of the skill in order for its
        # information to fully load
        course_percentage = self.data.current_skill / num_skills
        scroll = "window.scrollTo(0, document.body.scrollHeight * " + str(course_percentage) + ");"
        self.browser.execute_script(scroll)

        skill = skills[self.data.current_skill]

        skill_level = self.skill_level(skill)

        try:
            start_button = self.start_button(skill)
        except WebDriverException:
            self.browser.execute_script(scroll)
            start_button = self.start_button(skill)

        xp = self.find_xp_gain(start_button)
        current_sentences = len(self.data.sentence_dictionary)

        increment = self.will_be_finished(skill)

        self.click(start_button)
        self.complete_skill(skill_level, course_percentage)

        if increment:
            self.data.update_current_skill(
                (self.data.current_skill + 1) % num_skills)

        num_new_sentences = current_sentences - len(self.data.sentence_dictionary)

        return xp, num_new_sentences, increment
