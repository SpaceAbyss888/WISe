print('Please, before using script, read README.md')

from transformers import pipeline
import requests
import wikipediaapi

print('Looading model, please wait')
pipe = pipeline("text2text-generation", model="google/flan-t5-large")

headers = {
    "User-Agent": "wikiaisearch/0.1 (SpaceAbyss888@gmail.com)"
    # Headers for the requests library
}

user_agent = "wikiaisearch/0.1 (SpaceAbyss888@gmail.com)"
# User agent for wikipedia api

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent=user_agent
)
# This part of code creates wiki object to use its api.

def get_potential_article_name(question):
  return pipe(f"""
  You're a neural network for finding articles on Wikipedia. The user will ask questions like “When was Washington D.C. founded?” and you will have to identify the topic in that sentence, in this case the topic of the sentence is “Washington D.C.”.
  You should also emphasize a unique and narrow topic, not a general and covering a large number of concepts. For example, in the sentence “when was the Python language created”, the topic would be “Python programming language”

  Now, the user will give you his question.
  Question: {question}
  """)[0]['generated_text'] # This thing is able to find theme in users question

def get_correction_suggestion(query, lang="en"):
    """Get a spelling correction suggestion"""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 1,
        "format": "json"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return data[1][0] if data[1] else None # This function returns the EXACT name of article

def get_text(name):
  page = wiki.page(name)
  if page.exists():
      return page.summary
  else:
      print("Article not found") # this is kinda obvious

def question_answering(question, context):
  return pipe(f"""
  You need to answer my question using context. If you can't find answer in the context - don't answer the question and just say that you can't find answer

  Example:
  Question: What is the capital of France?
  Context: Paris is the capital of France, as well as the largest city in France.
  Answer: Paris is the capital of France.

  Now my question:
  Question: {question}
  Context: {context[:511]}
  Answer:
  """)[0]['generated_text'] # This function uses context from wiki article to answer the question.
                            # As you can see, it only uses first 512 symbols of article ( this is because of pipeline limitation, i will fix it later)

# Infinite loop so theres no need to run all the previous code
print('To exit infinite Q/A loop type "exit"')
while True:
  question = input("What\' your question?\n")
  if question == 'exit':
    break
  else:
    pot_an = get_potential_article_name(question)
    article_name = get_correction_suggestion(pot_an)
    context = get_text(article_name)
    print(f'Script used this article: {article_name}')
    print(question_answering(question, context))
