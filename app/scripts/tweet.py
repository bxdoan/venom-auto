# Desc: Tweet 20 words from the GPT-3.5 model
from app.chatgpt import tweet_20_words


if __name__ == '__main__':
    res = tweet_20_words()
    print(res)
