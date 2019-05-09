import tweepy
import time
import re
import requests

print('my twitter bot')

CONSUMER_KEY = '#'
CONSUMER_SECRET = '#'
ACCESS_KEY = '#'
ACCESS_SECRET = '#'
# Replace with your keys

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth,
                 wait_on_rate_limit=True)  # wait on rate limit allows it wait else it crashed if API limit reaches

mentions = api.mentions_timeline()

FILE_NAME = 'last_seen.txt'
USERS_FILE = 'users.txt'


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def storeUser(userID, city, file_name):
    f_write = open(file_name, 'a')
    f_write.write(str(userID + ',' + city + '\n'))
    f_write.close()
    return


def displayWeather():
    print('Retrieving and replying to tweets...')

    last_seen_id = retrieve_last_seen_id(FILE_NAME)

    mentions = api.mentions_timeline(last_seen_id,
                                     tweet_mode='extended')

    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#' in mention.full_text.lower():

            s = mention.full_text.lower()
            tags = re.findall(r"#(\w+)", s)


            if len(tags) is 1:
                print(tags)
                x = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={tags[0]}&APPID=YOURKEYHERE').json()
                if x['cod'] == 200:
                    print('200')
                    temperature = float(x['main']['temp'] - 273.15).__round__(0)
                    degree = '°C'
                    if mention.user.screen_name in open('users.txt').read():
                        print("User already present in file")
                    else:
                        print('tweeting back to user')
                        api.update_status(f'@{mention.user.screen_name} Weather for {tags[0]} is {temperature}{degree}')
                        storeUser(mention.user.screen_name, tags[0], USERS_FILE)
                        # my_list = line.split(",")
                else:
                    print('city not found')


while True:
    try:
        displayWeather()
        time.sleep(15)
    except tweepy.TweepError:
        time.sleep(2)
        continue
