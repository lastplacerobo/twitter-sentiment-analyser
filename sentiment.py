#!/usr/bin/env python3

import yaml
import TwitterSearch
import preprocessor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import OrderedDict
import datetime
import locale

# Set LC_TIME for datetime
locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


# Search tweets based on keyword and language
def tweet_search(keywords, tweet_lang):
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

        # Save all tweets in a nested dic
        # twitty{"id"}
        #          |- {date} -> tweet creation date
        #          |- {text} -> tweet text
        twitty = {}
        for tweet in ts.search_tweets_iterable(tso):
            # Dict based on tweet ID, assign a new dict as value
            twitty[tweet["id"]] = {}
            # Key is date and value "created at"
            twitty[tweet["id"]]["date"] = tweet["created_at"]
            # Key is text and value is the tweet
            twitty[tweet["id"]]["text"] = tweet["text"]

        return twitty

    except TwitterSearch.TwitterSearchException as e:
        print(e)


# Clean tweets from links and mentions
def tweet_sanitizer(tweets):
    for key, value in tweets.items():
        preprocessor.set_options(preprocessor.OPT.MENTION, preprocessor.OPT.URL)
        # Clean each tweet from mentions and URLs
        value["text"] = preprocessor.clean(value["text"])

    return tweets


# Run a sentiment analysis on each tweet, save each tweets compound score in list sentiment.
# the compound score shows the sentiment of the tweet
def sentiment_analyser(tweets):
    analyzer = SentimentIntensityAnalyzer()
    for key, value in tweets.items():
        vs = analyzer.polarity_scores(value["text"])
        # create a new nested key with the compound value for each tweet
        value["score"] = vs["compound"]

    return tweets


def plot_sentiment(sentiment, keyword):
    # Make a datetime object of each date entry
    for key, value in sentiment.items():
        value["date"] = datetime.datetime.strptime((value["date"]), '%a %b %d %H:%M:%S %z %Y')

    # Order the dic after date
    ordered = OrderedDict(sorted(sentiment.items(), key=lambda i: i[1]['date']))

    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(111)
    # Rotate xticks
    fig.autofmt_xdate()

    # positive: compound score >= 0.05
    # neutral: (compound score > -0.05) and (compound score < 0.05)
    # negative: compound score <= -0.05
    # -1 (most extreme negative) and +1 (most extreme positive)
    for key, value in ordered.items():

        if value["score"] >= 0.05:
            ax.scatter(value["date"], value["score"], color="darkgreen")

        elif value["score"] <= -0.05:
            ax.scatter(value["date"], value["score"], color="darkred")

        else:
            ax.scatter(value["date"], value["score"], color="aqua")

    darkgreen = mpatches.Patch(color='darkgreen', label='Positive')
    aqua = mpatches.Patch(color='aqua', label='Neutral')
    darkred = mpatches.Patch(color='darkred', label='Negative')

    ax.legend(loc="best", handles=[darkgreen, aqua, darkred])
    ax.set(title='Twitter Sentiment for: ' + str(keyword), xlabel='Date', ylabel='Sentiment')

    fig.tight_layout()
    plt.show()


def main():
    # all entities in the list must exist in the tweet, so only use one at a time
    keyword = ["semester"]
    tweet_lang = "sv"

    # Run tweet_search
    tweets = tweet_search(keyword, tweet_lang)

    # Run sentiment analysis
    sentiment = sentiment_analyser(tweet_sanitizer(tweets))

    # Plot the sentiment
    plot_sentiment(sentiment, keyword)


# Only run main if executed directly
if __name__ == "__main__":
    main()
