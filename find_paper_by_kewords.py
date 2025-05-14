import os
import codecs
import json
import sys
sys.path.append('./')
import time
import requests
import time
from typing import List, Dict, Union
from threading import Thread
import random
import arxiv
from fuzzywuzzy import fuzz
from random import choice

S2_API_KEY = ''

def search_for_papers(query, result_limit=10, publicationDateOrYear=None) -> Union[None, List[Dict]]:
    if not query:
        return None




    rsp = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        headers={"X-API-KEY": S2_API_KEY},
        params={
            "query": query,
            "limit": result_limit,
            "fields": "title,authors,year,abstract,citationCount,openAccessPdf,citations,citations.title,citations.year,citations.citationCount",
            'publicationDateOrYear': publicationDateOrYear,
        },
    )
    # rsp.raise_for_status()
    results = rsp.json()
    total = results["total"]
    time.sleep(1.5)
    if not total:
        return None

    papers = results["data"]
    return papers

def download(urls, save_path, time_sleep_in_seconds=5, is_random_step=True,
              verbose=False, proxy_ip_port=None):
    """
    download file from given urls and save it to given path
    :param urls: str, urls
    :param save_path: str, full path
    :param time_sleep_in_seconds: int, sleep seconds after call
    :param is_random_step: bool, whether random sample the time step between two
        adjacent download requests. If True, the time step will be sampled
        from Uniform(0.5t, 1.5t), where t is the given time_step_in_seconds.
        Default: True.
    :param verbose: bool, whether to display time step information.
        Default: False
    :param proxy_ip_port: str or None, proxy server ip address with or without
        protocol prefix, eg: "127.0.0.1:7890", "http://127.0.0.1:7890".
    :return: None
    """

    def __download(urls, save_path):
        head, tail = os.path.split(save_path)


        r = requests.get(urls, stream=True)


        if '' != head:
            os.makedirs(head, exist_ok=True)

        for part in r.iter_content(1024 ** 2):
            with open(save_path, 'ab') as file:
                file.write(part)
        r.close()
    t = Thread(
        target=__download, args=(urls, save_path), daemon=False)
    t.start()

    if is_random_step:
        time_sleep_in_seconds = random.uniform(
            0.5 * time_sleep_in_seconds,
            1.5 * time_sleep_in_seconds,
        )
    if verbose:
        print(f'\t random sleep {time_sleep_in_seconds: .2f} seconds')
    time.sleep(time_sleep_in_seconds)









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

def data_check(file_path, new_idex):
    if os.path.exists(file_path):
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            file.close()
    else:
        return False
    

    existing_indexes = {item["index"] for item in existing_data}

    if new_idex not in existing_indexes: 
        return False
    else:
        return True

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def clean_name(paper_name):
    return paper_name.replace("{", "").replace("{", "").replace("\texttt", "").replace("!", "").replace("+", "").replace("`", "").replace(")", "").replace("(", "").replace("\'", " ").replace("\"", "").replace("^", "").replace("$", "").replace("-", " ").replace(":", " ").replace("?", "").replace("&", "").replace(",", "").replace("/", " ").replace(".", " ").replace("  ", " ").replace("   ", " ").replace("    ", " ").lower()



def find_from_SC(search_results, cited_paper_store_paths, cited_paper_store_path, paper_local_paths):
    # paper_local_paths =[]
    exit_paper = list(paper_local_paths.keys())
    if search_results is not None:
        for paper in search_results:
                if paper['openAccessPdf']:
                    
                    if clean_name(paper['title'])+'.pdf' not in cited_paper_store_paths:
                        download(paper['openAccessPdf']['url'], os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf'))
                        
                        if os.path.exists(os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf')):
                            cited_paper_store_paths.append(os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf'))
                            paper_local_paths[os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf')] = paper['citationCount']
                    elif os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf') not in exit_paper:
                        paper_local_paths[os.path.join(cited_paper_store_path, clean_name(paper['title'])+'.pdf')] = paper['citationCount']                        

    return paper_local_paths, cited_paper_store_paths


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    summary_data_path = "../target_paper_data.json"
    if os.path.exists(summary_data_path):

        with codecs.open(summary_data_path, 'r', encoding='utf-8') as file:
            summary_datas = json.load(file)
            file.close()

    reuslt_w_hd_cd = "./dataset_temple/target_paper_data_w_hd_cd.json"

    cited_paper_store_path = './dataset_temple/paper_temple'

    cited_paper_store_paths = os.listdir(cited_paper_store_path)

    final_summary_data = []



    
    for summary_data in summary_datas:

        keywords = []
        print(summary_data['index'])
        for split_topic in summary_data['summary']['split_topic']:
            keywords.append(split_topic["keyword"])
        paper_hd_local_path = {}
        for i in range(len(keywords)):
            try:
                search_results = search_for_papers(', '.join(keywords[:-i]),result_limit=5,publicationDateOrYear=':2023-10-03')
            except Exception as e:
                print('Exception:', e)
                search_results =None
            time.sleep(1.5)
            if search_results:
                paper_hd_local_path, cited_paper_store_paths = find_from_SC(search_results, cited_paper_store_paths, cited_paper_store_path, paper_hd_local_path)
                if len(list(paper_hd_local_path.keys()))>=5:
                    break


        paper_cd_local_path = {}
        for i in range(len(keywords)):
            try:

                search_results = search_for_papers(', '.join(keywords[:-i]),result_limit=5,publicationDateOrYear='2023-10-03:')
            except Exception as e:
                print('Exception:', e)
                search_results =None
            time.sleep(1.5)
            if search_results:
                paper_cd_local_path, cited_paper_store_paths = find_from_SC(search_results, cited_paper_store_paths, cited_paper_store_path, paper_cd_local_path)

                if len(list(paper_cd_local_path.keys()))>=5:
                    break

        summary_data['summary']['paper_hd_local_path'] = paper_hd_local_path
        summary_data['summary']['paper_cd_local_path'] = paper_cd_local_path


        final_summary_data.append(summary_data)




    save_json(final_summary_data, reuslt_w_hd_cd)




    