from pathlib import Path
import time
from random import choice
from typing import List
from openai import OpenAI
import json
import re



import os


class  Deepseek:
    def __init__(self,api_key_list_deepseek, base_url_deepseek, model_name_deepseek="deepseek-chat", temperature_deepseek=0.6):
    

        self.api_key_list_deepseek = api_key_list_deepseek
        self.base_url_deepseek = base_url_deepseek



        self.model_name_deepseek = model_name_deepseek
        self.temperature_deepseek = temperature_deepseek

        
        

            
    def send_request(self, prompt, question):
        """
        """
        output = {}
        while True:
            try:



                api_key_deepseek = choice(self.api_key_list_deepseek)
                
                client_deepseek = OpenAI(api_key=api_key_deepseek, base_url=self.base_url_deepseek)






                messages = [
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {"role": "user", "content": question},
                ]

                output = client_deepseek.chat.completions.create(
                    model=self.model_name_deepseek,
                    messages=messages,
                    temperature=self.temperature_deepseek,
                    response_format={"type": "json_object"},
                    stream=False,
                    max_tokens=8000
                )
                output = self.postprocess(output)



                break
            except Exception as e:
                print('Exception:', e)



        return output

    def forward(self, prompt, question)->str:
        """
        """

        model_output = self.send_request(prompt, question)

        
        # time.sleep(2)
        return model_output
    
    def postprocess(self, output):
        """
        """
        model_output = None
        if isinstance(output, str):
            model_output = output
        else:

            # model_output = output.choices[0].message
            content = output.choices[0].message.content
            content = re.sub(r'```json\n|\n```', '', content)
            model_output = json.loads(content)
        return model_output

    def __call__(self, prompt:str, question:str):
        return self.forward(prompt, question)


