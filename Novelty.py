import codecs

import json

from sentence_transformers import SentenceTransformer


from statistics import mean
import os


def get_content_between_a_b(start_tag, end_tag, text):
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag) : end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()


def extract_json(text):
    if "```json" in text:
        target_str = get_content_between_a_b("```json", "```", text)
        return target_str
    else:
        return text

def extract(text, type1, type2, hard = True):
    if text:
        target_str = get_content_between_a_b(f"{type1}", f"{type2}", text)
        if target_str:
            return target_str
        elif hard:
            return text
        else:
            return ""
    else:
        return ""


def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    cited_paper_conten_path = "./dataset_temple/target_paper_data_w_hd_cd.json"
    if os.path.exists(cited_paper_conten_path):
        with codecs.open(cited_paper_conten_path, 'r', encoding='utf-8') as file:
            cited_papers_data_raw = json.load(file)
            file.close()

    cited_papers_data_all = {}
    cited_papers_data_index = {}
    for data_ in cited_papers_data_raw:

        curren_index_cited_paper_conten = {}
       
        for data in data_["model_result"]:
            cited_papers_data_all[data['paper_path']] = data['model_result']

            curren_index_cited_paper_conten[data['paper_path']] = data['model_result']

        cited_papers_data_index[data_['index']] = curren_index_cited_paper_conten



    topic_path = "./dataset_temple/target_paper_data_w_hd_cd.json"
    with codecs.open(topic_path, "r") as f:
        topics_ = json.load(f)
        f.close()  

    hd_local_papers = {}  #history

    cd_local_papers = {}  #curren

    for topic in topics_:

        hd_local_papers[topic["index"]] = topic["summary"]["paper_hd_local_path"]

        cd_local_papers[topic["index"]] = topic["summary"]["paper_cd_local_path"]


    model = SentenceTransformer('all-MiniLM-L6-v2')
#########################################################################################################################################


    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = []
    AI_Scientist_final_path = "./model_output/AI-Scientist/Novelty.json"
    for results in AI_Scientist_:
        fianl_result = []

        hd_local_paper_paths = list(hd_local_papers[results['index']].keys())
        cd_local_paper_paths = list(cd_local_papers[results['index']].keys())
        # topic = topics[results['index']]

        for result in results['model_result']:
            
            motivation = result['Motivation']
            Experiment_Plan = result['Experiment']
            
            pred_motivation_embeddings = model.encode(str(motivation))
            pred_experiment_plan_embeddings = model.encode(str(Experiment_Plan))

            motivation_similaritys = []
            experiment_similaritys = []

            cited_papers_data = cited_papers_data_index[results['index']]

            for paper in hd_local_paper_paths:
                if cited_papers_data[paper]['idea']:
                    current_motivation = cited_papers_data[paper]['idea']
                    current_experiment = cited_papers_data[paper]['experiment']
                    current_motivation_embeddings = model.encode(current_motivation)
                    current_experiment_embeddings = model.encode(current_experiment)

                    motivation_similarity_matrix = model.similarity(pred_motivation_embeddings, current_motivation_embeddings)

                    experiment_similarity_matrix = model.similarity(pred_experiment_plan_embeddings, current_experiment_embeddings)
                                    
                    motivation_similaritys.append(float(motivation_similarity_matrix[0][0]))

                    experiment_similaritys.append(float(experiment_similarity_matrix[0][0]))
            try:
                hd_motivation_similarity = mean(motivation_similaritys)
            except:
                hd_motivation_similarity=0
            
            try:
                hd_experiment_similarity = mean(experiment_similaritys)
            except:
                hd_experiment_similarity=0

            motivation_similaritys = []
            experiment_similaritys = []

            citations = []

            for paper in cd_local_paper_paths:
                if cited_papers_data[paper]['idea']:
                    current_motivation = cited_papers_data[paper]['idea']
                    current_experiment = cited_papers_data[paper]['experiment']
                    current_motivation_embeddings = model.encode(current_motivation)
                    current_experiment_embeddings = model.encode(current_experiment)

                    motivation_similarity_matrix = model.similarity(pred_motivation_embeddings, current_motivation_embeddings)

                    experiment_similarity_matrix = model.similarity(pred_experiment_plan_embeddings, current_experiment_embeddings)
                                    
                    motivation_similaritys.append(float(motivation_similarity_matrix[0][0]))

                    experiment_similaritys.append(float(experiment_similarity_matrix[0][0]))

                    citations.append(cd_local_papers[results['index']][paper])


            try:
                cd_motivation_similarity = mean(motivation_similaritys)
            except:
                cd_motivation_similarity=0
            
            try:
                cd_experiment_similarity = mean(experiment_similaritys)
            except:
                cd_experiment_similarity=0

            try:
                ci=mean(citations)
            except:
                ci=0

            on_motivation = (1+cd_motivation_similarity)*ci/(1+hd_motivation_similarity)
            on_experiment = (1+cd_experiment_similarity)*ci/(1+cd_motivation_similarity)


            split_result = {
                'on_motivation':on_motivation,
                'on_experiment':on_experiment
            }


            # split_result = None
            result['ON'] = split_result
            
            fianl_result.append(result)
        
        results['model_result'] = fianl_result

        AI_Scientist.append(results)

    save_json(AI_Scientist, AI_Scientist_final_path)

