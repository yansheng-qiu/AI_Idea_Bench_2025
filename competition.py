import random
from collections import defaultdict
import codecs
import json
import os


from LLM.Deepseek_v5 import Deepseek

from prompt_template.compare_open import get_judge_ideas_all_prompt



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

class Player:
    def __init__(self, name,idea):
        self.name = name
        self.score = 0
        self.opponents = set() 
        self.idea = idea

    def __repr__(self):
        return f"{self.name} (Score: {self.score})"


class SwissTournament:
    def __init__(self, players):
        self.players = players
        self.round = 0

    def pair_players(self):
        sorted_players = sorted(self.players, key=lambda x: x.score, reverse=True)
        paired_players = []
        used_players = set()

        for i, player1 in enumerate(sorted_players):
            if player1 in used_players:
                continue 
            for j in range(i + 1, len(sorted_players)):
                player2 = sorted_players[j]
                if player2 not in used_players and player2.name not in player1.opponents:
                    paired_players.append((player1, player2))
                    used_players.add(player1)
                    used_players.add(player2)
                    break
            else:
                for player2 in sorted_players:
                    if player2 not in used_players and player2.name not in player1.opponents:
                        paired_players.append((player1, player2))
                        used_players.add(player1)
                        used_players.add(player2)
                        break
                else:
                    for player2 in sorted_players:
                        if player2 not in used_players:
                            paired_players.append((player1, player2))
                            used_players.add(player1)
                            used_players.add(player2)
                            break

        return paired_players

    def play_round(self, topic, cline):
        self.round += 1
        pairs = self.pair_players()
        raw_choice = []
        for player1, player2 in pairs:


            if player1.name != player2.name:

                system_prompt, user_prompt = get_judge_ideas_all_prompt(player1.idea, player2.idea, topic)

                choice_result = cline(system_prompt, user_prompt)

                raw_choice.append({f"{player1.name} vs {player2.name}" : choice_result})

                result = choice_result['Final_choice']

                print(f"{player1.name} vs {player2.name}: {result}")
                if result == 0:
                    player1.score += 3
                    player2.score += 1
                else:
                    player1.score += 1
                    player2.score += 3
            else:
                player1.score += 0
                player2.score += 0        
                result = 0        
            player1.opponents.add(player2.name)
            player2.opponents.add(player1.name)

            
            

        return raw_choice
            

    def print_standings(self):
        print("\nCurrent Standings:")
        sorted_players = sorted(self.players, key=lambda x: x.score, reverse=True)
        ranking = {}
        # for index, item in enumerate(my_list):
        for player in sorted_players:
            ranking[player.name] = player.score
            # print(player)
        print(ranking)

        return ranking



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


if __name__ == "__main__":

    Topic_path =  "../target_paper_data.json"
    with codecs.open(Topic_path, "r") as f:
        Topics_ = json.load(f)
        f.close()

    Topics = {}
    for result in Topics_:
        if result["summary"]["revised_topic"]:
            Topics[result['index']]  = result["summary"]["revised_topic"]
        else:
            Topics[result['index']]  = result["summary"]["topic"]


    

    result_path = './swiss_result.json'

    AI_Researcher_path = "./model_output/AI-Researcher/final_ideas.json"
    with codecs.open(AI_Researcher_path, "r") as f:
        AI_Researcher_ = json.load(f)
        f.close()

    AI_Researcher = {}
    for result in AI_Researcher_:
        AI_Researcher[result['index']] = result['model_result']

    AI_Scientist_path = "./model_output/AI-Scientist/final_ideas.json"
    with codecs.open(AI_Scientist_path, "r") as f:
        AI_Scientist_ = json.load(f)
        f.close()

    AI_Scientist = {}
    for result in AI_Scientist_:
        AI_Scientist[result['index']] = result['model_result']


    SciPIP_path = "./model_output/SciPIP/final_ideas.json"
    with codecs.open(SciPIP_path, "r") as f:
        SciPIP_ = json.load(f)
        f.close()


    SciPIP = {}
    for result in SciPIP_:
        SciPIP[result['index']] = result['model_result']



    Social_Science_path = "./model_output/Social_Science/final_ideas.json"
    with codecs.open(Social_Science_path, "r") as f:
        Social_Science_ = json.load(f)
        f.close()

    Social_Science = {}
    for result in Social_Science_:
        Social_Science[result['index']] = result['model_result']



    assert AI_Researcher.keys() == AI_Scientist.keys() == Social_Science.keys() == SciPIP.keys() == CoI_Agent.keys()


    import random




    for index in AI_Researcher.keys(): 
        
        players = []


        AI_Researcher_idea = ''
        
        players.append(Player('AI_Researcher',  AI_Researcher_idea))


        #########################################################################################################################################

        temple_key = random.randint(0, len(AI_Scientist[index])-1)
        motivation = AI_Scientist[index][temple_key]['Motivation']
        Experiment_Plan = AI_Scientist[index][temple_key]['Experiment']
        AI_Scientist_idea = 'Motivation: ' + str(motivation)  + '/n' + 'Experiment_Plan: ' + str(Experiment_Plan) + '/n'
        
        players.append(Player('AI_Scientist', AI_Scientist_idea))

        #########################################################################################################################################


        SciPIP_idea = ''
        players.append(Player('SciPIP',  SciPIP_idea))

        #########################################################################################################################################


        Social_Science_idea = ''   
        players.append(Player('Social_Science', Social_Science_idea))


        #########################################################################################################################################

        api_key_deepseek = ''

        base_url_deepseek = ''

        model_api = Deepseek([api_key_deepseek], base_url_deepseek)

        if data_check(result_path, index):
            pass
        else:
            tournament = SwissTournament(players)

            raw_choices = []
            for _ in range(7): 
                raw_choice = tournament.play_round(Topics[index], model_api)
                raw_choices.append(raw_choice)

            ranking = tournament.print_standings()

            final_result = {'raw_choices':raw_choices, 'ranking':ranking}

            append_to_json_file(result_path, final_result, index)



