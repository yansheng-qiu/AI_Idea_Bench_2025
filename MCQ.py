import codecs

import json

from prompt_template.compare_gt import compare_motivation, compare_plan


from LLM.Deepseek_v5 import Deepseek




def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":



    api_key_deepseek = ""

    base_url_deepseek = "https://api.deepseek.com/v1" 

    model_name_deepseek = 'deepseek-chat'

    model_api = Deepseek([api_key_deepseek], base_url_deepseek, model_name_deepseek=model_name_deepseek)



    motivation_mcq_path = './dataset_temple/mcq_motivation.json'
    experiment_mcq_path = './dataset_temple/mcq_experiment_plan.json'
    with codecs.open(motivation_mcq_path, "r") as f:
        mot_mcqs_ = json.load(f)
        f.close()

    with codecs.open(experiment_mcq_path, "r") as f:
        exp_mcqs_ = json.load(f)
        f.close()

    mot_mcqs = {}

    exp_mcqs = {}


    for mot_mcq in mot_mcqs_:
        mot_mcqs[mot_mcq['index']] = mot_mcq['mcq']


    for exp_mcq in exp_mcqs_:
        exp_mcqs[exp_mcq['index']] = exp_mcq['mcq']






#########################################################################################################################################        


    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = []
    AI_Scientist_final_path = "./model_output/AI-Scientist/MCQ.json"
    for results in AI_Scientist_:
        fianl_result = []
        current_mot_mcq = mot_mcqs[results['index']]
        current_mot_a = current_mot_mcq["question"]['a']
        current_mot_b = current_mot_mcq["question"]['b']
        current_mot_c = current_mot_mcq["question"]['c']
        current_mot_d = current_mot_mcq["question"]['d']
        current_mot_answer = current_mot_mcq["answer_option"]
        

        current_exp_mcq = exp_mcqs[results['index']]
        current_exp_a = current_exp_mcq["question"]['a']
        current_exp_b = current_exp_mcq["question"]['b']
        current_exp_c = current_exp_mcq["question"]['c']
        current_exp_d = current_exp_mcq["question"]['d']
        current_exp_answer = current_exp_mcq["answer_option"]
        # topic = topics[results['index']]

        for result in results['model_result']:
            
            motivation = result['Motivation']
            Experiment_Plan = result['Experiment']
            
            system_prompt, user_prompt = compare_motivation(motivation, option_a=current_mot_a, option_b=current_mot_b, option_c=current_mot_c, option_d=current_mot_d)
            mot_result = model_api(system_prompt, user_prompt)


            system_prompt, user_prompt = compare_plan(Experiment_Plan, plan_a=current_exp_a, plan_b=current_exp_b, plan_c=current_exp_c, plan_d=current_exp_d)
            exp_result = model_api(system_prompt, user_prompt)

            split_result = {
                'mot_result':{'prediction':mot_result, 'gt':current_mot_answer},
                'exp_result':{'prediction':exp_result, 'gt':current_exp_answer}
            }

            result['MCQ'] = split_result
            
            fianl_result.append(result)
        
        results['model_result'] = fianl_result

        AI_Scientist.append(results)

    save_json(AI_Scientist, AI_Scientist_final_path)

########################################################################################################################################

