import sys
import time
import traceback

sys.path.append('../duolingo')
from duolingo import Duolingo
from selenium.common.exceptions import WebDriverException

def try_intro(session):
    if session.data.current_skill == 0:
        try:
            session.start_intro()
        except WebDriverException:
            pass

def main(session):

    session.browser.get("https://www.duolingo.com/learn")

    session.log_in('odeeogbfrpysdkgxbj@bvhrs.com', 'PZrmkxbamu3eUA9')

    while not session.is_on_homepage():
        time.sleep(2)

    bubble_completed = False
    empty_handed_count = 0
    current_total_mined = 0
    skill_no = 0
    while empty_handed_count < 10:
        passes = 0
        while passes < 6:
            xp, sentences_mined, bubble_completed = session.do_next_skill(skill_no, False)
            print(sentences_mined)
            current_total_mined += sentences_mined
            if bubble_completed:
                passes += 1
        skill_no += 1
        if current_total_mined == 0:
            empty_handed_count += 1
        else:
            empty_handed_count = 0

    session.save()
    print("You've stripped the mine!")

session = Duolingo('german', covert=False, humanize=False)
if __name__ == '__main__':
    try:
        main(session)
    except BaseException as error:
        if not error.__class__.__name__ == 'KeyboardInterrupt':
            print(repr(error))
            traceback.print_exc()
        session.save()
