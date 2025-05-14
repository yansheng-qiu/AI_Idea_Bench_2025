
import argparse
import json
from LLM.Deepseek_v3 import Deepseek
import codecs
import os
import asyncio
import random

import scipdf
import PyPDF2
from SementicSearcher import SementicSearcher
from threading import Thread

from prompt_template.process_one_paper import get_deep_reference_prompt
import arxiv
from fuzzywuzzy import fuzz
import time

import requests
import time
from typing import List, Dict, Union
import aiohttp


import urllib
import random
from urllib.error import URLError, HTTPError

import fitz  # PyMuPDF

from extract_one_paper_conten import get_one_paper_conten



def save_json(data, file_path):
    with open(file_path, 'a') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def data_check(file_path, new_idex):
    if os.path.exists(file_path):
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            file.close()
    else:
        return False
    

    existing_indexes = [item["paper_path"] for item in existing_data]

    if new_idex not in existing_indexes: 
        return False
    else:
        return True


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def append_to_json_file(file_path, new_data, index):
    if os.path.exists(file_path):
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            file.close()
    else:
        existing_data = []

    existing_data.append(
        {
        "index": index,
        "model_result": new_data
        }
        )

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
    print("Data appended successfully.")


class Result:
    def __init__(self,title="",abstract="",article=None,citations_conut = 0,year = None) -> None:
        self.title = title
        self.abstract = abstract
        self.article = article
        self.citations_conut = citations_conut
        self.year = year




if __name__ == "__main__":

    api_key_deepseek = ''
    base_url_kimi = ''
    base_url_deepseek = ''


    model_api = Deepseek([api_key_deepseek], base_url_deepseek)




    find_cite_result_directory = "./dataset_temple/target_paper_data_w_hd_cd.json"

    with codecs.open(find_cite_result_directory, "r") as f:
        paper_paths = json.load(f)
        f.close()

    cited_paper_conten_path = "./dataset_temple/hd_cd_paper_conten.json"



    paper_need_redownload = []

    for paper_path in paper_paths:
        seed_paper_path = []

        paper_local_path = list(paper_path['summary']['paper_hd_local_path'].keys())

        paper_local_path.extend(list(paper_path['summary']['paper_cd_local_path'].keys()))

        if paper_path["summary"]["revised_topic"]:

            topic = paper_path["summary"]["revised_topic"]
        
        else:

            topic = paper_path["summary"]["topic"]


        hd_cd_paper_data = []
        for cited in paper_local_path:


            LLM_result = None

            if cited:
                print(cited)
                pdf_path = cited

                try:


                    LLM_result = get_one_paper_conten(model_api, pdf_path, topic)
                    hd_cd_paper_data.append({"paper_path":topic,
                                "model_result":LLM_result})

                except Exception as e:
                    print('Exception:', e)

                    LLM_result = None
            else:
                LLM_result = None


            output_json = {}
            if LLM_result is not None:
                pass
            else:
                if cited:
                    paper_need_redownload.append(cited)


        append_to_json_file(cited_paper_conten_path, LLM_result, paper_path['index'])





    paper_need_redownload_path  = 'paper_need_redownload.json'

    paper_need_redownload_ = {}

    paper_need_redownload_['redonwload'] = paper_need_redownload

    save_json(paper_need_redownload_, paper_need_redownload_path)

    




