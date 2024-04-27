import openai 
import config

openai.api_key = config.api_key

response = openai.ChatCompletion.create(model="gpt-3.5-turbo", 
                                        messages=[{"role": "user", "content":"Me puedes explicar la teoría de cuerdas de forma clara y sencilla?"}])

print("------------------------------------------------------")

print(response.choices[0].message.content)