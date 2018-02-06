import sys
import praw
import logging
import matplotlib
import time
import datetime
import pprint
import json

# subreddit to get stats for
subreddit = ''
# search range for posts and comments
start_date = "01/01/2017"
end_date = "01/01/2018"

threads = 4
users = {}

# Get some logging going
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('root')


#Login to Reddit
try:
    reddit = praw.Reddit()
except Exception as e:
    logger.error(e)
    logger.error('Reddit login failed')


#Convert Human Readable dates to Unix timestamps
start = time.mktime(datetime.datetime.strptime(start_date, "%d/%m/%Y").timetuple())
end = time.mktime(datetime.datetime.strptime(end_date, "%d/%m/%Y").timetuple())

#If your start is after your end, exit
if start > end:
    logger.error('Start date is after end date.')
    exit(2)

#If dates are the same, add 24 hours to get the full day.
if start == end:
    end = end + (24 * 60 * 60)
    logger.debug('DEBUG: Start and end date is the same.  Adding 24 hours to end date to get full day.')

# try to login to reddit
try:
    sr = reddit.subreddit(subreddit)
except Exception as e:
    logger.error(e)
    exit(3)

print('Gathering users from {0} to {1}'.format(start_date, end_date))

# Get submissions in tiome range
submissions = list(sr.submissions(start, end))
total_submissions = len(submissions)
logger.info('Total submissions: {}'.format(total_submissions))
print("Total submissions: {}".format(total_submissions))

submission_count = 0
comment_count = 0

# Get all comments for submission and record each user name.
for submission in submissions:
    logger.info('Processing submission id {}'.format(str(submission.id)))
    #make sure to grab all comments
    submission.comments.replace_more(limit=None, threshold=0)
    logger.info('Number of comments: {}'.format(len(submission.comments.list())))
    #Go down each comment and get the username
    for comment in submission.comments.list():
        try:
            if comment.author not in users:
                users[str(comment.author)] = {}
            comment_count += 1
        except Exception as e:
            logger.error(e)
            logger.error('Cant add user from comment to dict')
            logger.error('Attempted comment: {}'.format(str(comment)))
    submission_count += 1

    sys.stdout.write("\rSubmissions, Comments processed: {0}, {1}".format(submission_count,comment_count))
sys.stdout.write("\n")

print("Users Gathered: {}".format(len(users)))
print("Gathering User data")
user_count = 0

#for each user, get max new and top comments and submissions and record which subreddit each is in.
for user in users:
    redditor = reddit.redditor(user)
    try:
        user_new_comments = list(redditor.comments.new(limit=None))
    except Exception as e:
        logger.error(e)
    try:
        user_new_submissions = list(redditor.submissions.new(limit=None))
    except Exception as e:
        logger.error(e)
    try:
        user_top_comments = list(redditor.comments.top(limit=None))
    except Exception as e:
        logger.error(e)
    try:
        user_top_submissions = list(redditor.submissions.top(limit=None))
    except Exception as e:
        logger.error(e)

    users[user]['new_comment_sr_count'] = {}
    for comment in user_new_comments:
        if comment.subreddit.display_name in users[user]['new_comment_sr_count']:
            users[user]['new_comment_sr_count'][str(comment.subreddit.display_name)] += 1
        else:
            users[user]['new_comment_sr_count'][str(comment.subreddit.display_name)] = 1

    users[user]['new_submission_sr_count'] = {}
    for submission in user_new_submissions:
        if submission.subreddit.display_name in users[user]['new_submission_sr_count']:
            users[user]['new_submission_sr_count'][str(submission.subreddit.display_name)] += 1
        else:
            users[user]['new_submission_sr_count'][str(submission.subreddit.display_name)] = 1

    users[user]['top_comment_sr_count'] = {}
    for comment in user_top_comments:
        if comment.subreddit.display_name in users[user]['top_comment_sr_count']:
            users[user]['top_comment_sr_count'][str(comment.subreddit.display_name)] += 1
        else:
            users[user]['top_comment_sr_count'][str(comment.subreddit.display_name)] = 1

    users[user]['top_submission_sr_count'] = {}
    for submission in user_top_submissions:
        if submission.subreddit.display_name in users[user]['top_submission_sr_count']:
            users[user]['top_submission_sr_count'][str(submission.subreddit.display_name)] += 1
        else:
            users[user]['top_submission_sr_count'][str(submission.subreddit.display_name)] = 1
    user_count += 1
    sys.stdout.write("\rUsers processed: {}".format(user_count))
sys.stdout.write("\n")

with open('user_data.json', 'w') as file:
    json.dump(users, file)

pprint.pprint(users)

exit(0)