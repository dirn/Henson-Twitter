from henson import Application
from henson_twitter import Twitter


async def callback(app, message):
    print()
    print()
    print(message['user']['name'], 'said')
    print(message['text'])
    print()
    print()


class Settings:
    TWITTER_CONSUMER_KEY = 'ubY46rv7Qe353NZgKdqrg'
    TWITTER_CONSUMER_SECRET = 'Gy6o3rtWSL4qlD3FdD6narwB1xEr2zG5OJ46HqPE'
    TWITTER_FILTER = {'track': '#wednesdaywisdom'}
    TWITTER_OAUTH_TOKEN = '314909425-v5upk2UmJEiCxSi5vhMRRGBZTtExKQGsqXXhL3Ct'
    TWITTER_OAUTH_TOKEN_SECRET = 'NdqqEf68YSCHxFTzbSpPijM7PO5PmlBbZlX4Z64'


app = Application('tweeter', Settings, callback=callback)
twitter = Twitter(app)


if __name__ == '__main__':
    app.run_forever(debug=True)
