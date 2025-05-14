import codecs

import json

from prompt_template.compare_open import create_experiment_evaluation_prompt

from LLM.Deepseek_v5 import Deepseek




def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    api_key_deepseek = ''
    base_url_deepseek = ''

    model_api = Deepseek([api_key_deepseek], base_url_deepseek)



    

#########################################################################################################################################        


    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = []
    AI_Scientist_final_path = "./model_output/AI-Scientist/EP-MOT.json"
    for results in AI_Scientist_:
        fianl_result = []

        for result in results['model_result']:
            
            motivation = result['Motivation']
            Experiment_Plan = result['Experiment']
            system_prompt, user_prompt = create_experiment_evaluation_prompt(motivation, Experiment_Plan)
            split_result = model_api(system_prompt, user_prompt)
            result['EP-MOT'] = split_result
            
            fianl_result.append(result)
        
        results['model_result'] = fianl_result

        AI_Scientist.append(results)

    save_json(AI_Scientist, AI_Scientist_final_path)

########################################################################################################################################


 