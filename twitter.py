#streamlit
#pandas
#snscrape
#pymongo

import streamlit as st
import pandas as pd
import snscrape.modules.twitter as sntwitter
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['twitter']

keyword = "Elon Musk"
start_date = "2023-02-15"
end_date = "2023-04-03"
limit = 1000
def scrape_twitter_data(keyword, start_date, end_date, limit):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} since:{start_date} until:{end_date}').get_items()):
        if i >= limit:
            break
        tweet_dict = {
            'date': tweet.date,
            'id': tweet.id,
            'url': tweet.url,
            'content': tweet.content,
            'user': tweet.user.username,
            'reply_count': tweet.replyCount,
            'retweet_count': tweet.retweetCount,
            'language': tweet.lang,
            'source': tweet.sourceLabel,
            'like_count': tweet.likeCount
        }
        tweets.append(tweet_dict)
    
    db[keyword].insert_many(tweets)
    return pd.DataFrame(tweets)


# Set up the sidebar
st.sidebar.title('Twitter Scraper')
keyword = st.sidebar.text_input('Enter a keyword or hashtag to search for:')
start_date = st.sidebar.date_input('Start date:')
end_date = st.sidebar.date_input('End date:')
limit = st.sidebar.slider('Limit:', 1, 1000, 100)

# Set up the main page
st.title('Twitter Scraper')
if keyword:
    st.write(f'Scraping tweets containing "{keyword}"...')
    data = scrape_twitter_data(keyword, start_date, end_date, limit)
    st.write(data)
    
    if st.button('Upload to MongoDB'):
        db[keyword].insert_many(data.to_dict('records'))
        st.success(f'Successfully uploaded {len(data)} tweets to MongoDB!')
    
    file_format = st.selectbox('Choose a file format to download:', ('CSV', 'JSON'))
    if st.button('Download'):
        if file_format == 'CSV':
            data.to_csv(f'{keyword}.csv', index=False)
            st.success(f'Successfully downloaded {len(data)} tweets as CSV!')
        else:
            data.to_json(f'{keyword}.json', orient='records')
            st.success(f'Successfully downloaded {len(data)} tweets as JSON!')


if __name__ == '__main__':
    st.set_page_config(page_title='Twitter Scraper')
    st.cache(persist=True)
    run()


