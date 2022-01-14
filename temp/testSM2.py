from supermemo2 import SMTwo
from datetime import datetime, timedelta

quality = 1
today = datetime.today()
yesterday = today - timedelta(days=1)
tmrw = today + timedelta(days=1)
print('date ', today)

review_obj = SMTwo.first_review(quality, yesterday)
print(type(review_obj))

print(review_obj.easiness)
print(review_obj.interval) 
# change to actual date, also change how interval is calculated to make intervals smaller than a day (10 minutes)
# the interval between the latest review date and the next review date.

print(review_obj.repetitions) 
# the count of consecutive reviews with quality larger than 2.

review_obj.review(3, today)
print(review_obj.easiness)
print(review_obj.interval) 
print(review_obj.repetitions) 

review_obj.review(5, tmrw)
print(review_obj.easiness)
print(review_obj.interval) 
print(review_obj.repetitions) 
