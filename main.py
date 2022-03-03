from re import search
from os import getenv
from time import sleep

from pymysql import connect, Error
from connector import Connector

from praw import Reddit
from praw.exceptions import PRAWException, APIException

SUBREDDIT = getenv('subreddit')

# local array to store the submission IDs
SUBMISSION_ID = []
CONN = Connector()


# Connect to database
def db_conn():
    try:
        with CONN.get_conn() as cursor:
            # connect to the database. if it doesn't exist, automatically create.
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS submissionTable(submissionID TEXT)')  # create tables if they dont exist
            cursor.execute('SELECT submissionID from submissionTable')
            moredata = cursor.fetchall()
            for row in moredata:
                SUBMISSION_ID.append(row[0])  # add the submission ids to the local variable
    except Error as er:
        print(str(er))


# Authenticate with Reddit
def authenticate():
    try:
        reddit = Reddit(client_id=getenv('client_id'),
                        client_secret=getenv('client_secret'),
                        password=getenv('password'),
                        user_agent=getenv('user_agent'),
                        username=getenv('username'))
        reddit.validate_on_submit = True
        return reddit
    except PRAWException as pr:
        print(str(pr))


def try_get_seconds_to_wait(ex_msg):
    try:
        msg = ex_msg.lower()
        srch = search(r'\b(minutes)\b', msg)
        minutes = int(msg[srch.start() - 2]) + 1
        return minutes * 60
    except:
        return 60


def process_submission(submission):
    if submission.id in SUBMISSION_ID:  # if the posts id is already in our database, ignore.
        return None
    else:
        try:
            with CONN.get_conn() as cursor:
                submission.downvote()
                submission.reply('Вам лгут. Сдавайтесь, пока вы еще можете \n You are being lied to. Give up while you still can. \n SLAVA UKRAINI')
                submission.report('SLAVA UKRAINI 🇺🇦')
                SUBMISSION_ID.append(submission.id)  # add the submission id to our variable
                cursor.execute('INSERT INTO submissionTable VALUES (%s)', [submission.id])
                print(f'Processed submission with id {submission.id}')
                return
        except TypeError as e:
            print(str(e))
        except APIException as er:
            secs = try_get_seconds_to_wait(str(er))
            print(f'Sleeping for {secs} seconds.')
            sleep(secs)


def main():
    if authenticate():
        print('Logged into Reddit!')
        while True:
            for submission in authenticate().subreddit(SUBREDDIT).new(limit=35):
                process_submission(submission)


if __name__ == '__main__':
    main()
