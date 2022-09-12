import sys
import random
import time
from datetime import datetime, timedelta
import traceback

sys.path.append('../duolingo')
from duolingo import Duolingo
from selenium.common.exceptions import WebDriverException

# Hards stops: 955-11 (lesson), 12:30-1:30 (bubble), 3:23-4:03 (lesson), 6:10-8:24 (bubble), 11:02 (bubble)
# Minute, second, hard=false
STOPS = [(9, 55, True), (12, 30, False), (15,23, True), (18, 10, False), (23, 2, False)]

def get_next_stop(now):
    for stop in STOPS:
        if now.hour < stop[0] or (now.hour == stop[0] and now.minute < stop[1]):
            return stop
    return None


def get_end_time():
    now = datetime.now()
    cutoff = get_next_stop(now)
    if cutoff:
        cutoff_time = now.replace(hour=cutoff[0], minute=cutoff[1], second=0, microsecond=0)
        is_hard_stop = cutoff[2]
    else:
        cutoff_time = datetime.max
        is_hard_stop = False
    h = 1
    m = random.randint(42, 91)
    s = random.randint(0, 60)
    ms = random.randint(0, 1000000)
    session_length = timedelta(hours=h, minutes=m, seconds=s, microseconds=ms)
    end_time = now + session_length
    if end_time > cutoff_time:
        end_time = cutoff_time
    return end_time, is_hard_stop

def try_intro():
    if session.data.current_skill == 0:
        try:
            session.start_intro()
        except WebDriverException:
            pass

def main(session):
    end_time, is_hard_cutoff = get_end_time()

    session.browser.get("https://www.duolingo.com/learn")

    session.log_in('odeeogbfrpysdkgxbj@bvhrs.com', 'PZrmkxbamu3eUA9')

    while not session.is_on_homepage():
        time.sleep(2)

    bubble_completed = False
    while datetime.now() < end_time or (not is_hard_cutoff and not bubble_completed):
        xp_gained, sentences_mined, bubble_completed = session.do_next_skill()
        if xp_gained <= 0:
            break

    checkpoint = 0
    while datetime.now() < end_time:
        session.browser.get("https://www.duolingo.com/checkpoint/hv/" + str(checkpoint) + "/practice")
        session.complete_skill(5, .33 * checkpoint)
        checkpoint = (checkpoint + 1) % 3

    session.save()
    print("Sun is getting real low")

if __name__ == '__main__':
    session = Duolingo('high_valyrian', covert=True, humanize=False)
    try:
        main(session)
    except BaseException as error:
        if not error.__class__.__name__ == 'KeyboardInterrupt':
            print(repr(error))
            traceback.print_exc()
        session.save()
