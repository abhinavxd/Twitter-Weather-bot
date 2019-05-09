import tweepy
import time
import re
import requests
import schedule
import traceback

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

FILE_NAME = 'last_seen1.txt'
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


def storeuser(userID, city, mentionid):
    f_write = open(USERS_FILE, 'a')
    f_write.write(str(userID + ',' + city + ',' + str(mentionid) + '\n'))
    f_write.close()
    return


def getWeather(city):
    x = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID=YOURKEYHERE').json()
    return float(x['main']['temp'] - 273.15).__round__(0)


def displayWeather():
    try:
        print('Retrieving and replying to tweets...')

        last_seen_id = retrieve_last_seen_id(FILE_NAME)

        mentions = api.mentions_timeline(last_seen_id,
                                         tweet_mode='extended')

        for mention in reversed(mentions):
            print(str(mention.id) + ' - ' + mention.full_text)
            last_seen_id = mention.id
            store_last_seen_id(last_seen_id, FILE_NAME)
            if '#' in mention.full_text.lower():
                if '#unsub' not in mention.full_text.lower():
                    s = mention.full_text.lower()
                    tags = re.findall(r"#(\w+)", s)

                    if len(tags) is 1:
                        x = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={tags[0]}'
                                         f'&APPID=YOURKEYHERE').json()
                        if x['cod'] == 200:
                            temperature = getWeather(tags[0])
                            degree = '°C'
                            if mention.user.screen_name in open(USERS_FILE).read():
                                print("User already present in file")
                                with open(USERS_FILE, 'r') as file:
                                    lines = file.readlines()
                                # now we have an array of lines.

                                for idx, val in enumerate(lines):
                                    if mention.user.screen_name in val:
                                        lines[idx] = f'{mention.user.screen_name},{tags[0]},{mention.id}\n'
                                with open(USERS_FILE, 'w') as file:
                                    file.writelines(lines)
                            else:
                                print('tweeting back to user')
                                api.update_status(f'@{mention.user.screen_name} Weather for {tags[0]} is '
                                                  f'{temperature}{degree}, You have successfully subscribed, '
                                                  f'you will receive 1 tweet daily with the weather details'
                                                  f'. Use #unsub to unsubscribe anytime.', mention.id)
                                storeuser(mention.user.screen_name, tags[0], mention.id)
                                # my_list = line.split(",")
                        else:
                            print('city not found')
                else:
                    with open(USERS_FILE, "r") as infile:
                        lines = infile.readlines()

                        for pos, line in enumerate(lines):
                            if mention.user.screen_name in line:
                                lines[pos] = ''
                        with open(USERS_FILE, 'w') as file:
                            file.writelines(lines)
                    api.update_status(f'@{mention.user.screen_name} Unsubscribed!', mention.id)
    except Exception as ex:
        traceback.print_exc()

def scheduledweather():
    try:
        print('in scheduled weather')
        with open(USERS_FILE) as f:
            for line in f:
                my_list = line.split(",")
                degree = '°C'
                temperature = getWeather(my_list[1])
                mentionid = my_list[2].replace('\n', '')
                api.update_status(f'@{my_list[0]} Weather for {my_list[1]} is {temperature}{degree}', mentionid)
                print('sent!!')
    except:
        print('Error')


# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
schedule.every().day.at("11:00").do(scheduledweather)
schedule.every().minute.at(":30").do(displayWeather)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)

    except tweepy.TweepError:
        time.sleep(2)
        continue
