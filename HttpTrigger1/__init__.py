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

    response_json = {
        "joke": joke,
        "gif_url": gif_url,
        "search_nouns": " ".join(filtered_nouns)
    }

    return func.HttpResponse(json.dumps(response_json), mimetype='application/json')
