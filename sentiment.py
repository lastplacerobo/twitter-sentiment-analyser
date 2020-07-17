#!/usr/bin/env python3

import yaml
import TwitterSearch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def tweetsearch(keywords, tweet_lang):
    # load yaml file with secrets to dictionary
    credentials = yaml.safe_load(open("./credentials.yml"))

    try:
        tso = TwitterSearch.TwitterSearchOrder()  # create a TwitterSearchOrder object
        tso.set_keywords(keywords)  # defines all words that we like to search for in a tweet
        tso.set_language(tweet_lang)  # set the language of tweets we are searching for
        tso.set_include_entities(False)  # no entity information

        # create a TwitterSearch object with our secret tokens
        ts = TwitterSearch.TwitterSearch(
            consumer_key=credentials['database']['consumer_key'],
            consumer_secret=credentials['database']['consumer_secret'],
            access_token=credentials['database']['access_token'],
            access_token_secret=credentials['database']['access_token_secret']
        )

        # Save all tweets in a list and return it
        all_tweets = []
        for tweet in ts.search_tweets_iterable(tso):
            all_tweets.append(tweet['text'])
        return all_tweets

    except TwitterSearch.TwitterSearchException as e:  # take care of all those ugly errors if there are some
        print(e)


# All entities in the list must exist in the tweet, so only use one at a time
keyword = ["EVO"]
tweet_lang = "sv"

# Run tweetsearch and save them in a list
tweets = tweetsearch(keyword, tweet_lang)

# run a sentiment analysis on each tweet, save each tweets compound score in list sentiment.
# the compound score shows the sentiment of the tweet
sentiment = []
analyzer = SentimentIntensityAnalyzer()
for tweet in tweets:
    vs = analyzer.polarity_scores(tweet)
    sentiment.append(vs["compound"])

# positive: compound score >= 0.05
# neutral: (compound score > -0.05) and (compound score < 0.05)
# negative: compound score <= -0.05
# -1 (most extreme negative) and +1 (most extreme positive)

# Test the sentiment
positive = 0
negative = 0
neutral = 0
for sent in sentiment:

    if sent >= 0.05:
        positive += 1

    elif sent <= -0.05:
        negative += 1

    else:
        neutral += 1

print(keyword, "Total Tweets:", len(tweets), "\n")
print("Positive Tweets:", positive)
print("Negative Tweets:", negative)
print("Neutral Tweets:", neutral)

