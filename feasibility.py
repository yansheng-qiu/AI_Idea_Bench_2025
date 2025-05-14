
import json
import codecs
import time
import requests
import time
from typing import List, Dict, Union
import time
from tqdm import tqdm
from statistics import mean

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
    rsp.raise_for_status()
    results = rsp.json()
    total = results["total"]
    time.sleep(1.5)
    if not total:
        return None

    papers = results["data"]
    return papers



def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


import math

def normalize(x):
    return -math.exp(-x / 50) + 1


def feasibility(keywords):
    try_count = 0
    while True:
        try:
            paper_data = search_for_papers(keywords, result_limit=5, publicationDateOrYear=None)
            time.sleep(0.5)
            break
        except Exception as e:
            print(e)
            time.sleep(3)
            try_count += 1

            if try_count >3:
                paper_data = None
                break
    fb = 0
    if paper_data:
        for paper in paper_data:

            recently_cite = 0

            cite_year = {}

            for citation in paper['citations']:

                if citation['year'] in [2025, 2024, 2023]:

                    recently_cite += 1

                else:
                    if citation['year'] in list(cite_year.keys()):
                        cite_year[citation['year']] += 1
                    else:
                        cite_year[citation['year']] = 1

        fb = fb + normalize(recently_cite)

        for year_key in cite_year.keys():
            if year_key:
                fb = fb + normalize(cite_year[year_key])/(2024-year_key)
    return fb


if __name__ == "__main__":

#########################################################################################################################################        


    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas_splited.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = []
    AI_Scientist_final_path = "./model_output/AI-Scientist/final_ideas_splited_feasibility.json"
    for results in tqdm(AI_Scientist_, desc="Processing model results"):
        fianl_result = []

        for result in results['model_result']:
            
            split_results = result['splited_kewords']

            all_fb = []
            
            for split_result in split_results['experiment_plan']:
                keywords= ', '.join(split_result["methods"])
                fb = feasibility(keywords)
                all_fb.append(fb)

                
            result['feasibility'] = all_fb  

            fianl_result.append(result)
 
        results['model_result'] = fianl_result

        AI_Scientist.append(results)

    save_json(AI_Scientist, AI_Scientist_final_path)

#######################################################################################################################################

