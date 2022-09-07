import sys
import time
import traceback

sys.path.append('../duolingo')
from duolingo import Duolingo
from selenium.common.exceptions import WebDriverException


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

def practice_checkpoint(session):
    session.browser.get("https://www.duolingo.com/learn")
    session.log_in('odeeogbfrpysdkgxbj@bvhrs.com', 'PZrmkxbamu3eUA9')
    time.sleep(7)
    while True:
        session.browser.get("https://www.duolingo.com/checkpoint/hv/2/practice")
        session.complete_skill(100, .33)
    session.save()

if __name__ == '__main__':
    session = Duolingo('high_valyrian')
    try:
        main(session)
    except BaseException as error:
        if not error.__class__.__name__ == 'KeyboardInterrupt':
            print(repr(error))
            traceback.print_exc()
        session.save()
