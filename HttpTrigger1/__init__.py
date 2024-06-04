import logging
import requests
import json
import spacy
import os

import azure.functions as func

# function that filters nouns
def noun_filter(noun):
    if noun == "Chuck Norris":
        return False
    if len(noun) == 1:
        return False
    return True

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # get the joke
    res = requests.get('https://api.chucknorris.io/jokes/random')
    response = json.loads(res.text)
    joke = response['value']

    # get the nouns from the joke
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(joke)

    # filter out Chuck Norris himself as well as single letter nouns
    nouns = [chunk.text for chunk in doc.noun_chunks]
    filtered_nouns = [noun for noun in nouns if noun_filter(noun)]
    giphy_query = "+".join(filtered_nouns).replace(" ", "+")[:50]

    # get the first gif from Giphy
    url = f"https://api.giphy.com/v1/gifs/search?api_key={os.environ['GIPHY_API_KEY']}&q={giphy_query}&limit=1&offset=0&rating=g&lang=en&bundle=messaging_non_clips"
    res = requests.get(url)
    response = json.loads(res.text)
    gif_url = response['data'][0]['images']['original']['url']

    html = """
    <html>
        <head>
            <title>Chuck Norris Joke</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" />
        </head>
        <body style="margin: 100px auto; max-width: 500px;">
            <h1>Chuck Norris Joke</h1>
            <p>{joke}</p>
            <p>Source: <a href="https://api.chucknorris.io/jokes/random">https://api.chucknorris.io/jokes/random</a></p>
            <img src={gif_url} alt="{nouns}" width="500" height="600">
        </body>
    </html>
    """.format(joke=joke, gif_url=gif_url, nouns=" ".join(filtered_nouns))

    return func.HttpResponse(html, mimetype='text/html')
