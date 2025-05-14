import codecs

import json



from prompt_template.compare_gt import similarity_experiment_plan_w_experiment_plan, similarity_motivation_w_motivation


from LLM.Deepseek_v5 import Deepseek


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

    api_key_deepseek = ''
    base_url_deepseek = ''

    model_api = Deepseek([api_key_deepseek], base_url_deepseek)

    topic_path = './target_paper_data.json'
    with codecs.open(topic_path, "r") as f:
        topics_ = json.load(f)
        f.close()  


    motivations = {}
    for topic_ in topics_:
        motivations[topic_['index']] = topic_['model_result']['motivation']


    experiments = {}
    for topic_ in topics_:
        experiments_ = topic_['model_result']['method']['targeted_designs_details']
        experiment_plan = ''
        for ex in experiments_:

            experiment_plan = experiment_plan + ex['design_name'] + ': ' + ex['description'] + '\n'

        experiments[topic_['index']] = experiment_plan


#########################################################################################################################################        


    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = []
    AI_Scientist_final_path = "./model_output/AI-Scientist/IGI.json"
    for results in AI_Scientist_:
        fianl_result = []


        motivation_gt = motivations[results['index']]

        experiment_gt = experiments[results['index']]
        # topic = topics[results['index']]

        for result in results['model_result']:
            
            motivation = result['Motivation']
            Experiment_Plan = result['Experiment']
            #
            system_prompt, user_prompt = similarity_experiment_plan_w_experiment_plan(experiment_plan1=Experiment_Plan, experiment_plan2=experiment_gt)

            m2m = model_api(system_prompt, user_prompt)


            system_prompt, user_prompt = similarity_motivation_w_motivation( motivation1=motivation, motivation2=motivation_gt)

            e2e = model_api(system_prompt, user_prompt)


            result['IGI'] = {
                "motivation_similarity":m2m,
                "experiment_plan_similarity":e2e
            }
            
            fianl_result.append(result)
        
        results['model_result'] = fianl_result

        AI_Scientist.append(results)

    save_json(AI_Scientist, AI_Scientist_final_path)

