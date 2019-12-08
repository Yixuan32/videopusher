from apscheduler.schedulers.background import BackgroundScheduler
import time


def job():
    print('job 3s')


if __name__=='__main__':
    sched = BackgroundScheduler(timezone='EST')
    sched.add_job(job, 'cron', day_of_week='mon-sun', hour=0, minute=42)
    sched.start()
    while (True):
        print()
        time.sleep(10)

