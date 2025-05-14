import sys
import os
import json
import codecs
from sentence_transformers import SentenceTransformer
import numpy as np
import random



def data_check(file_path, new_idex):
    if os.path.exists(file_path):
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            file.close()
    else:
        return False
    

    existing_indexes = [item["index"] for item in existing_data]
    if new_idex not in existing_indexes: 
        return False
    else:
        return True





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
        "mcq": new_data
        }
        )
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
    print("Data appended successfully.")



if __name__ == "__main__":

    cited_paper_conten_path = "./dataset_temple/cited_paper_conten.json"
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





    find_cite_result_directory = "./target_paper_data.json"

    with codecs.open(find_cite_result_directory, "r") as f:
        cited_paper_paths_ = json.load(f)
        f.close()

    cited_paper_paths = {}


    curren_indexs = []

    for cite_paper_path in cited_paper_paths_:
        paper_paths = []

        curren_indexs.append(cite_paper_path['index'])

        for paper_path in cite_paper_path['find_cite']['top_references']:

            if paper_path['paper_local_path']:
                paper_paths.append(paper_path['paper_local_path'])

        cited_paper_paths[cite_paper_path['index']] = paper_paths


    summary_data_path = "./target_paper_data.json"
    if os.path.exists(summary_data_path):
        with codecs.open(summary_data_path, 'r', encoding='utf-8') as file:
            summary_datas = json.load(file)
            file.close()
    
    motivation_gt_all = []
    experiment_plan_gt_all = []
    index_all = []
    for summary_data in summary_datas:
        index = summary_data['index']
        print('index:', index)
        index_all.append(index)
        motivation_gt = summary_data['summary']['motivation']

        motivation_gt_all.append(motivation_gt)

        experiments_ = summary_data['summary']['method']['targeted_designs_details']
        experiment_plan_gt = ''
        step = 1
        for ex in experiments_:

                
            experiment_plan_gt = experiment_plan_gt + ex['design_name'] + ': ' + ex['description'] + '\n'
        
        experiment_plan_gt_all.append(experiment_plan_gt)

    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    mcq_motivation_path = "./dataset_temple/mcq_motivation.json"
    for i in range(len(motivation_gt_all)):
        
        curren_index = index_all[i]

        print(curren_index)


        cited_paper_paths_ = cited_paper_paths[curren_index]

        curren_cited_paper_conten = cited_papers_data_index[curren_index]

        

        current_embeddings = model.encode(motivation_gt_all[i])

        cited_similarity_results = []
        cited_motivations = []
        for cite_paper_path in cited_paper_paths_:
            paper_data = curren_cited_paper_conten[cite_paper_path]
            cited_motivation = paper_data['idea']
            if cited_motivation:
                cited_motivations.append(cited_motivation)
                cited_embeddings = model.encode(cited_motivation)
                cited_similarity_matrix = model.similarity(current_embeddings, cited_embeddings)
                cited_similarity_results.append(float(cited_similarity_matrix[0][0]))


        cited_similarity_results = np.array(cited_similarity_results)
        top_2_indices = np.argpartition(-cited_similarity_results, 2)
        top1_index_,top2_index_ = top_2_indices
        option_one = cited_motivations[top1_index_]
        option_two = cited_motivations[top2_index_]



        cited_similarity_results = []
        cited_motivations = []
        for cite_paper_path in cited_papers_data_all:
            if cite_paper_path not in curren_cited_paper_conten:
                paper_data = cited_papers_data_all[cite_paper_path]
                cited_motivation = paper_data['idea']
                if cited_motivation:
                    cited_motivations.append(cited_motivation)
                    cited_embeddings = model.encode(cited_motivation)
                    cited_similarity_matrix = model.similarity(current_embeddings, cited_embeddings)
                    cited_similarity_results.append(float(cited_similarity_matrix[0][0]))


        cited_similarity_results = np.array(cited_similarity_results)
        top_1_indices = np.argpartition(-cited_similarity_results, 1)
        top3_index_ = top_1_indices
        option_three = cited_motivations[top3_index_]
        values = [motivation_gt_all[i], option_one, option_two, option_three]
        answer = values[0]
        random.shuffle(values)
        options = {
            'a': values[0],
            'b': values[1],
            'c': values[2],
            'd': values[3]
        }
        answer_option = [key for key, value in options.items() if value == answer][0]

        mcq = {
            'question': options,
            'answer_option':answer_option
        }



        if data_check(mcq_motivation_path, curren_index):
            pass
        else:
            append_to_json_file(mcq_motivation_path, mcq, curren_index)

    
    mcq_experiment_plan_path = "./dataset_temple/mcq_experiment_plan.json"
    for i in range(len(experiment_plan_gt_all)):
        curren_index = index_all[i]
        cited_paper_paths_ = cited_paper_paths[curren_index]
        current_embeddings = model.encode(experiment_plan_gt_all[i])

        cited_similarity_results = []
        cited_experiments = []
        for cite_paper_path in cited_paper_paths_:
            paper_data = cited_papers_data_all[cite_paper_path]
            cited_experiment = paper_data['experiment']
            if cited_experiment:
                cited_experiments.append(cited_experiment)
                cited_embeddings = model.encode(cited_experiment)
                cited_similarity_matrix = model.similarity(current_embeddings, cited_embeddings)
                cited_similarity_results.append(float(cited_similarity_matrix[0][0]))





        cited_similarity_results = np.array(cited_similarity_results)
        top_2_indices = np.argpartition(-cited_similarity_results, 2)
        top1_index_,top2_index_ = top_2_indices
        option_one = cited_experiments[top1_index_]
        option_two = cited_experiments[top2_index_]



        cited_similarity_results = []
        cited_experiments = []
        for cite_paper_path in cited_papers_data_all:
            if cite_paper_path not in curren_cited_paper_conten:
                paper_data = cited_papers_data_all[cite_paper_path]
                cited_motivation = paper_data['idea']
                if cited_motivation:
                    cited_experiments.append(cited_motivation)
                    cited_embeddings = model.encode(cited_motivation)
                    cited_similarity_matrix = model.similarity(current_embeddings, cited_embeddings)
                    cited_similarity_results.append(float(cited_similarity_matrix[0][0]))


        cited_similarity_results = np.array(cited_similarity_results)
        top_1_indices = np.argpartition(-cited_similarity_results, 1)
        top3_index_ = top_1_indices
        option_three = cited_experiments[top3_index_]

        values = [motivation_gt_all[i], option_one, option_two, option_three]
        answer = values[0]
        random.shuffle(values)
        options = {
            'a': values[0],
            'b': values[1],
            'c': values[2],
            'd': values[3]
        }
        answer_option = [key for key, value in options.items() if value == answer][0]

        mcq = {
            'question': options,
            'answer_option':answer_option
        }


        if data_check(mcq_experiment_plan_path, curren_index):
            pass
        else:
            append_to_json_file(mcq_experiment_plan_path, mcq, curren_index)

