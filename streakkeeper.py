import time
import traceback

from process import humanizer
from data.data_storage import DataStorage

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

class Duolingo (object):
    def __init__ (self, learning_language, known_language='english', humanize=False):
        self.browser = webdriver.Safari()
        self.data = DataStorage(learning_language)

        self.LEARNING_LANGUAGE = learning_language
        self.KNOWN_LANGUAGE = known_language
        self.HUMANIZE = humanize

        self.browser.maximize_window()

    def log_in(self, username, password):

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

        email_field.send_keys(username)

        password_field = self.browser.find_element(By.XPATH,
                                             '//input[@data-test="password-input"]')
        password_field.send_keys(password)

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
            button = WebDriverWait(self.browser, 1).until(
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

    def will_be_finished(self, skill):
        try:
            level_text = skill.find_element(By.CSS_SELECTOR, 'div._1m77f').text
            if level_text == 'Legendary Level':
                return True

            # Level 4/6
            fraction_1 = level_text.split(' ')[1]
            fraction_1_array = fraction_1.split('/')
            is_on_last_level = int(fraction_1_array[0]) + 2 == int(fraction_1_array[1])

            # Lesson 4/5
            lesson_text = skill.find_element(By.CSS_SELECTOR, 'div.RXDIm').text
            fraction_2 = lesson_text.split(' ')[1]
            fraction_2_array = fraction_2.split('/')
            is_on_last_lesson = int(fraction_2_array[0]) + 1 == int(fraction_2_array[1])

            return is_on_last_level and is_on_last_lesson
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

    def find_prompt_language(self):
        prompt = WebDriverWait(session.browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-test="challenge-header"]'))).text
        assert prompt[:14] == 'Write this in ', 'Unusual translation prompt'
        language = prompt[14:].replace(' ', '_').lower()
        if language == self.KNOWN_LANGUAGE:
            return self.LEARNING_LANGUAGE
        elif language == self.LEARNING_LANGUAGE:
            return self.KNOWN_LANGUAGE
        else:
            raise Exception('unknown language prompted for translation')

    def get_misc_answer(self, prompt):
        self.skip()
        solution = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//div[@class="_1UqAr _3Qruy"]'))).text

        self.data.add_other(prompt, solution)

    def save(self):
        print("Closing files")

        self.data.write_sentences()
        self.data.write_other()

        self.data.write_current_skill()

    def challenge_translate(self, skill_level, course_percentage, reverse=False):

        sentence = self.browser.find_element(By.XPATH, '//div[@class="_1KUxv _11rtD"]').text
        if not reverse:
            sentence_language = self.find_prompt_language()
            is_known_language = sentence_language == self.KNOWN_LANGUAGE
        else:
            print(sentence)
            sentence_language = self.KNOWN_LANGUAGE
            is_known_language = True

        if sentence in self.data.sentence_dictionary[sentence_language]:

            try:
                input_field = self.browser.find_element(By.XPATH,'//textarea[@data-test="challenge-translate-input"]')
            except WebDriverException:
                self.use_keyboard()
                input_field = self.browser.find_element(By.XPATH,'//textarea[@data-test="challenge-translate-input"]')

            answer = self.data.sentence_dictionary[sentence_language][sentence]
            if self.HUMANIZE:
                processed_answer, wait_time = humanizer(answer, is_known_language, 'translate', skill_level, course_percentage)
                time.sleep(wait_time)
                input_field.send_keys(processed_answer)
            else:
                input_field.send_keys(answer)
            input_field.send_keys(Keys.RETURN)

        else:
            self.skip()

            solution = self.browser.find_element(By.XPATH,
                                           '//div[@class="_1UqAr _3Qruy"]').text

            if (self.alt_solution_check(solution)):
                solution = solution[17:]


            if reverse:
                print(sentence, solution, sentence_language)
            self.data.add_sentence(sentence, solution, sentence_language)

        self.go_next()

    def challenge_select(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH,
                                       '//h1[@data-test="challenge-header"]').text
        sentence += " (s)"
        if sentence in self.data.other_dictionary:
            choices = self.browser.find_elements(By.XPATH, '//span[@class="HaQTI"]')

            answer_found = False
            for choice in choices:
                if choice.text in self.data.other_dictionary[sentence]:
                    answer_found = True
                    choice.click()
            if not answer_found:
                self.get_misc_answer(sentence)

        else:
            self.get_misc_answer(sentence)

        self.go_next()

    def challenge_form(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH,
                                       '//div[@class="_2SfAl _2Hg6H"]').get_attribute('data-prompt')
        sentence += " (f)"
        if sentence in self.data.other_dictionary:
            choices = self.browser.find_elements(By.XPATH, '//div[@data-test="challenge-judge-text"]')
            answer_found = False
            for choice in choices:
                if choice.text in self.data.other_dictionary[sentence]:
                    answer_found = True
                    choice.click()
            if not answer_found:
                self.get_misc_answer(sentence)

        else:
            self.get_misc_answer(sentence)

        self.go_next()

    def challenge_name(self, skill_level, course_percentage):
        sentence = self.browser.find_element(By.XPATH, '//h1[@data-test="challenge-header"]').text
        sentence += " (n)"
        if sentence in self.data.other_dictionary:
            input_field = self.browser.find_element(By.XPATH, '//input[@data-test="challenge-text-input"]')
            input_field.send_keys(self.data.other_dictionary[sentence][0])
            input_field.send_keys(Keys.RETURN)

        else:
            self.get_misc_answer(sentence)

        self.go_next()

    def challenge_partial_reverse_translate(self, skill_level, skill_no):
        input_field = self.browser.find_element(By.XPATH, '//span[@spellcheck="False"]')
        answer = self.browser.find_element(By.XPATH, '//span[@class="_1yM6s _1vqO5"]').text
        input_field.send_keys(answer)
        input_field.send_keys(Keys.RETURN)

    def complete_skill(self, level, course_percentage):

        skill_completed = False

        while not skill_completed:
            while True:
                time.sleep(.4)
                try:
                    challenge = session.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-translate"]')

                    self.challenge_translate(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-select"]')
                    self.challenge_select(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-form"]')
                    self.challenge_form(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    try:
                        challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-name"]')
                    except:
                        challenge = self.browser.find_element(By.XPATH, '//div[@data-test="ge challenge-name"]')

                    self.challenge_name(level, course_percentage)
                    continue
                except WebDriverException:
                    pass

                try:
                    challenge = self.browser.find_element(By.XPATH, '//div[@data-test="challenge challenge-completeReverseTranslation"]')
                    self.challenge_translate(level, course_percentage, True)
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
                    pass

                try:
                    no_thanks = self.browser.find_element(By.XPATH, '//button[@data-test="plus-no-thanks"]')
                    no_thanks.click()
                except WebDriverException:
                    pass

                try:
                    no_thanks_2 = self.browser.find_element(By.XPATH, '//button[@class="WOZnx _275sd _1ZefG _47xRj U1P3s _40EaN"]')
                    no_thanks_2.click()
                except WebDriverException:
                    pass

                try:
                    maybe_later = self.browser.find_element(By.XPATH, '//button[@data-test="maybe-later"]')
                    maybe_later.click()
                except WebDriverException:
                    pass

                try:
                    piss_off = self.browser.find_element(By.XPATH, '//button[@data-test="plus-close-x"]')
                    break
                    piss_off.click()
                except WebDriverException:
                    pass

                try:
                    start_preview = self.browser.find_element(By.XPATH, '//button[@class="_3HhhB _2NolF _275sd _1ZefG _3bnKZ _1Rcu8 _3PMUi"]')
                    if button.text == 'Start my free preview':
                        button.click()
                except WebDriverException:
                    pass

            time.sleep(4)
            try:
                self.browser.find_element(By.XPATH, '//button[@data-test="notification-drawer-no-thanks-button"]').click()
            except:
                pass
            try:
                self.browser.find_element(By.XPATH, '//div[@data-test="close-button"]').click()
            except:
                pass

    def learn_bot(self):
        while True:

            skills = WebDriverWait(self.browser, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-test="skill"]')))
            num_skills = len(skills)

            # Scroll to appoximate location of the skill in order for its information to fully load
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

            if xp <= 0:
                print("Where'd all the XP go?")
                break

            increment = self.will_be_finished(skill)

            start_button.click()
            self.complete_skill(skill_level, course_percentage)

            if increment:
                self.data.update_current_skill((self.data.current_skill + 1) % num_skills)


session = Duolingo('high_valyrian')

def main(session):

    session.browser.get("https://www.duolingo.com/learn")

    session.log_in('odeeogbfrpysdkgxbj@bvhrs.com', 'PZrmkxbamu3eUA9')

    while not session.is_on_homepage():
        time.sleep(2)

    if session.data.current_skill == 0:
        try:
            session.start_intro()
        except WebDriverException:
            pass

    session.learn_bot()

    session.save()

try:
    main(session)
except BaseException as error:
    if not error.__class__.__name__ == 'KeyboardInterrupt':
        print(repr(error))
        traceback.print_exc()
    session.save()
