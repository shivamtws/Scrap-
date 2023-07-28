import requests
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import openai
API_KEY = "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"

def content(text):
    # print("Text", text)
    openai.api_key = API_KEY

    prompt = f"Create an Instagram caption without hashtags according to this text: \n{text} and make sure the words approx 50"
    

    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50)

    if 'choices' in response and len(response['choices']) > 0:
        caption = response['choices'][0]['text'].strip()

        prompt = f"Generate 15 hashtags related to:\n{caption}\n\nHashtags:"
        hashtags_response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
        hashtags = [hashtag.strip() for hashtag in hashtags_response['choices'][0]['text'].split('\n')]

        prompt = f"Generate location suggestion for:\n{caption}\n\nLocation:"
        location_response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50)
        location = location_response['choices'][0]['text'].strip()

        prompt = f"Generate tag people suggestions for:\n{caption}\n\nTag people:"
        tag_people_response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
        tag_people = [person.strip() for person in tag_people_response['choices'][0]['text'].split('\n')]

        return caption, hashtags, location, tag_people

    return "Couldn't generate a caption.", [], "", []

def index(request):
    if request.method == "POST":
        url = request.POST.get("url")
        if url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for elem in soup(['script', 'style']):
                        elem.extract()
                    main_text = soup.get_text()
                    main_text = main_text.strip()
                    if len(main_text) > 10000:
                        strip_text = main_text[100:9000]
                        # strip_text.strip()
                        # print("##",strip_text,len(strip_text))
                        caption, hashtags, location, tag_people = content(strip_text)
                    else:
                        caption, hashtags, location, tag_people = content(main_text)

                    
                    # print(type(hashtags),"hashtags")
                    # print(type(tag_people),"tag_people")
                    return render(request, 'index.html', {
                        
                        'url': main_text,
                        'instagram_caption': caption,
                        'hashtags': hashtags,
                        'location': location,
                        'tag_people': tag_people
                    })

                else:
                    print(f"Error: Unable to fetch URL. Status code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

    return render(request, 'index.html')
