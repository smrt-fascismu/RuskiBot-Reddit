from os import getenv
from pymysql import connect, Error

from praw import Reddit
from praw.exceptions import PRAWException

SUBREDDIT = getenv('subreddit')

# local array to store the submission IDs
SUBMISSION_ID = []


# Connect to database
def db_conn():
    try:
        _conn = connect(user=getenv('db_user'), host=getenv('db_host'), port=int(getenv('db_port')),
                        password=getenv('db_password'), database=getenv('db'))
        # connect to the database. if it doesn't exist, automatically create.
        _cursor = _conn.cursor()
        _cursor.execute(
            'CREATE TABLE IF NOT EXISTS submissionTable(submissionID TEXT)')  # create tables if they dont exist
        _cursor.execute('SELECT submissionID from submissionTable')
        moredata = _cursor.fetchall()
        for row in moredata:
            SUBMISSION_ID.append(row[0])  # add the submission ids to the local variable
        return _conn, _cursor
    except Error as er:
        exit(str(er))


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
        exit(str(pr))


def process_submission(submission):
    conn, cursor = db_conn()
    if submission.id in SUBMISSION_ID:  # if the posts id is already in our database, ignore.
        return None
    else:
        try:
            submission.downvote()
            submission.reply('SLAVA UKRAINI 🇺🇦')
            submission.report('SLAVA UKRAINI')
            SUBMISSION_ID.append(submission.id)  # add the submission id to our variable
            cursor.execute('INSERT INTO submissionTable VALUES (%s)', [submission.id])
            # insert the comment and submission id into the database.
            conn.commit()  # commit the change
            print(f'Processed submission with id {submission.id}')
            return
        except Exception as e:
            exit(str(e))


def main():
    if authenticate():
        print('Logged into Reddit!')
        while True:
            for submission in authenticate().subreddit(SUBREDDIT).new(limit=35):
                process_submission(submission)


if __name__ == '__main__':
    main()
