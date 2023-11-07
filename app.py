from flask import Flask, render_template, request
import os
from googleapiclient.discovery import build
import re
from textblob import TextBlob
import matplotlib.pyplot as plt

app = Flask(__name__)
api_key = 'AIzaSyAi0Nf0SRVYuRh_8aixWO4PQmhnmfSeP1Q'  
youtube = build('youtube', 'v3', developerKey=api_key)

def clean_comment(comment):
    cleaned_comment = re.sub(r'[^a-zA-Z0-9\s,.!?]', '', comment)
    return cleaned_comment

def get_video_comments(video_id):
    comments = []

    nextPageToken = None

    while True:
        results = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            pageToken=nextPageToken
        ).execute()

        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            cleaned_comment = clean_comment(comment)
            comments.append(cleaned_comment)

        nextPageToken = results.get('nextPageToken')

        if not nextPageToken:
            break
    return comments

def analyze_sentiment(comments):
    positive_count = 0
    neutral_count = 0
    negative_count = 0

    for comment in comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            positive_count += 1
        elif polarity < 0:
            negative_count += 1
        else:
            neutral_count += 1

    total_count = len(comments)

    positive_percentage = (positive_count / total_count) * 100
    neutral_percentage = (neutral_count / total_count) * 100
    negative_percentage = (negative_count / total_count) * 100

    return positive_percentage, neutral_percentage, negative_percentage

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_id = request.form['video_id']
        comments = get_video_comments(video_id)
        positive_percentage, neutral_percentage, negative_percentage = analyze_sentiment(comments)

        positive_percentage = round(positive_percentage, 2)
        neutral_percentage = round(neutral_percentage, 2)
        negative_percentage = round(negative_percentage, 2)

        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [positive_percentage, neutral_percentage, negative_percentage]
        colors = ['green', 'lightgray', 'red']

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
        plt.axis('equal') 
        plt.title('Sentiment Analysis Results')

        chart_path = 'static/chart.png'
        plt.savefig(chart_path)
        plt.close()

        return render_template('result.html', video_id=video_id, positive=positive_percentage, neutral=neutral_percentage, 
        negative=negative_percentage, chart_path=chart_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
