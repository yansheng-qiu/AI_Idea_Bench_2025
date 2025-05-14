import json
import os
import os.path as osp
import time
from typing import List, Dict, Union

import backoff
import requests

import codecs

from ai_scientist.llm import get_response_from_llm, extract_json_between_markers, create_client, AVAILABLE_LLMS


import sys
sys.path.append('../../code/')  # change to your code path
from prompt_template.process_one_paper import get_one_paper_input

from extract_one_paper_conten import get_one_paper_conten


from LLM.Deepseek_v3 import Deepseek






idea_first_prompt = """{task_description}

Here are contens of related papers:

'''
{prev_ideas_string}
'''

Come up with the next impactful and creative idea for research experiments and directions you can feasibly investigate with the contens of related papers provided.
Note that you will not have access to any additional resources or datasets.
Make sure any idea is not overfit the specific training dataset or model, and has wider significance.

Respond in the following format:

THOUGHT:
<THOUGHT>

NEW IDEA JSON:
```json
<JSON>
```

In <THOUGHT>, first briefly discuss your intuitions and motivations for the idea. Detail your high-level plan, necessary design choices and ideal outcomes of the experiments. Justify how the idea is different from the existing ones.

In <JSON>, provide the new idea in JSON format with the following fields:
- "Name": A shortened descriptor of the idea. Lowercase, no spaces, underscores allowed.
- "Title": A title for the idea, will be used for the report writing.
- "Motivation":Provide a background for your idea, summarizing relevant past work. Identify shortcomings in previous research and highlight the specific problems that remain unsolved and that you aim to address.
- "Experiment": An outline of the implementation. E.g. which functions need to be added or modified, how results will be obtained, ...
- "Interestingness": A rating from 1 to 10 (lowest to highest).
- "Feasibility": A rating from 1 to 10 (lowest to highest).
- "Novelty": A rating from 1 to 10 (lowest to highest).

Be cautious and realistic on your ratings.
This JSON will be automatically parsed, so ensure the format is precise.
You will have {num_reflections} rounds to iterate on the idea, but do not need to use them all.
"""

idea_reflection_prompt = """Round {current_round}/{num_reflections}.
In your thoughts, first carefully consider the quality, novelty, and feasibility of the idea you just created.
Include any other factors that you think are important in evaluating the idea.
Ensure the idea is clear and concise, and the JSON is the correct format.
Do not make things overly complicated.
In the next attempt, try and refine and improve your idea.
Stick to the spirit of the original idea unless there are glaring issues.

Respond in the same format as before:
THOUGHT:
<THOUGHT>

NEW IDEA JSON:
```json
<JSON>
```

If there is nothing to improve, simply repeat the previous JSON EXACTLY after the thought and include "I am done" at the end of the thoughts but before the JSON.
ONLY INCLUDE "I am done" IF YOU ARE MAKING NO MORE CHANGES."""


# GENERATE IDEAS
def generate_ideas(
        input_paper,
        rearch_topic,
        client,
        model,
        max_num_generations=20,
        num_reflections=5,
        
):

    idea_str_archive = []


    idea_system_prompt = 'You are an ambitious AI PhD student who is looking to publish a paper that will contribute significantly to the field.'

    task_description = 'You are given the following file to work with. The rearch topic is: ' + rearch_topic

    for _ in range(max_num_generations):
        print(f"Generating idea {_ + 1}/{max_num_generations}")
        try:
            prev_ideas_string = input_paper

            msg_history = []
            print(f"Iteration 1/{num_reflections}")
            text, msg_history = get_response_from_llm(
                idea_first_prompt.format(
                    task_description=task_description,
                    prev_ideas_string=prev_ideas_string,
                    num_reflections=num_reflections,
                ),
                client=client,
                model=model,
                system_message=idea_system_prompt,
                msg_history=msg_history,
            )
            ## PARSE OUTPUT
            json_output = extract_json_between_markers(text)
            assert json_output is not None, "Failed to extract JSON from LLM output"
            print(json_output)

            # Iteratively improve task.
            if num_reflections > 1:
                for j in range(num_reflections - 1):
                    print(f"Iteration {j + 2}/{num_reflections}")
                    text, msg_history = get_response_from_llm(
                        idea_reflection_prompt.format(
                            current_round=j + 2, num_reflections=num_reflections
                        ),
                        client=client,
                        model=model,
                        system_message=idea_system_prompt,
                        msg_history=msg_history,
                    )
                    ## PARSE OUTPUT
                    json_output = extract_json_between_markers(text)
                    assert (
                            json_output is not None
                    ), "Failed to extract JSON from LLM output"
                    print(json_output)

                    if "I am done" in text:
                        print(f"Idea generation converged after {j + 2} iterations.")
                        break

            idea_str_archive.append(json.dumps(json_output))
        except Exception as e:
            print(f"Failed to generate idea: {e}")
            continue

    ## SAVE IDEAS
    ideas = []
    for idea_str in idea_str_archive:
        ideas.append(json.loads(idea_str))


    return ideas


# GENERATE IDEAS OPEN-ENDED
def generate_next_idea(
        base_dir,
        client,
        model,
        prev_idea_archive=[],
        num_reflections=5,
        max_attempts=10,
):
    idea_archive = prev_idea_archive
    original_archive_size = len(idea_archive)

    print(f"Generating idea {original_archive_size + 1}")

    if len(prev_idea_archive) == 0:
        print(f"First iteration, taking seed ideas")
        # seed the archive on the first run with pre-existing ideas
        with open(osp.join(base_dir, "seed_ideas.json"), "r") as f:
            seed_ideas = json.load(f)
        for seed_idea in seed_ideas[:1]:
            idea_archive.append(seed_idea)
    else:
        with open(osp.join(base_dir, "experiment.py"), "r") as f:
            code = f.read()
        with open(osp.join(base_dir, "prompt.json"), "r") as f:
            prompt = json.load(f)
        idea_system_prompt = prompt["system"]

        for _ in range(max_attempts):
            try:
                idea_strings = []
                for idea in idea_archive:
                    idea_strings.append(json.dumps(idea))
                prev_ideas_string = "\n\n".join(idea_strings)

                msg_history = []
                print(f"Iteration 1/{num_reflections}")
                text, msg_history = get_response_from_llm(
                    idea_first_prompt.format(
                        task_description=prompt["task_description"],
                        code=code,
                        prev_ideas_string=prev_ideas_string,
                        num_reflections=num_reflections,
                    )
                    + """
Completed ideas have an additional "Score" field which indicates the assessment by an expert ML reviewer.
This is on a standard 1-10 ML conference scale.
Scores of 0 indicate the idea failed either during experimentation, writeup or reviewing.
""",
                    client=client,
                    model=model,
                    system_message=idea_system_prompt,
                    msg_history=msg_history,
                )
                ## PARSE OUTPUT
                json_output = extract_json_between_markers(text)
                assert json_output is not None, "Failed to extract JSON from LLM output"
                print(json_output)

                # Iteratively improve task.
                if num_reflections > 1:
                    for j in range(num_reflections - 1):
                        print(f"Iteration {j + 2}/{num_reflections}")
                        text, msg_history = get_response_from_llm(
                            idea_reflection_prompt.format(
                                current_round=j + 2, num_reflections=num_reflections
                            ),
                            client=client,
                            model=model,
                            system_message=idea_system_prompt,
                            msg_history=msg_history,
                        )
                        ## PARSE OUTPUT
                        json_output = extract_json_between_markers(text)
                        assert (
                                json_output is not None
                        ), "Failed to extract JSON from LLM output"
                        print(json_output)

                        if "I am done" in text:
                            print(
                                f"Idea generation converged after {j + 2} iterations."
                            )
                            break

                idea_archive.append(json_output)
                break
            except Exception as e:
                print(f"Failed to generate idea: {e}")
                continue

    ## SAVE IDEAS
    with open(osp.join(base_dir, "ideas.json"), "w") as f:
        json.dump(idea_archive, f, ensure_ascii=False, indent=4)

    return idea_archive


def on_backoff(details):
    print(
        f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries "
        f"calling function {details['target'].__name__} at {time.strftime('%X')}"
    )


@backoff.on_exception(
    backoff.expo, requests.exceptions.HTTPError, on_backoff=on_backoff
)
def search_for_papers(query, result_limit=10) -> Union[None, List[Dict]]:
    if not query:
        return None
    rsp = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        headers={"X-API-KEY": os.environ["S2_API_KEY"]},
        params={
            "query": query,
            "limit": result_limit,
            "fields": "title,authors,venue,year,abstract,citationStyles,citationCount",
            'publicationDateOrYear': '2010-01-01:2023-10-03',
        },
    )
    rsp.raise_for_status()
    results = rsp.json()
    total = results["total"]
    time.sleep(1.0)
    if not total:
        return None

    papers = results["data"]
    return papers


novelty_system_msg = """You are an ambitious AI PhD student who is looking to publish a paper that will contribute significantly to the field.
You have an idea and you want to check if it is novel or not. I.e., not overlapping significantly with existing literature or already well explored.
Be a harsh critic for novelty, ensure there is a sufficient contribution in the idea for a new conference or workshop paper.
You will be given access to the Semantic Scholar API, which you may use to survey the literature and find relevant papers to help you make your decision.
The top 10 results for any search query will be presented to you with the abstracts.

You will be given {num_rounds} to decide on the paper, but you do not need to use them all.
At any round, you may exit early and decide on the novelty of the idea.
Decide a paper idea is novel if after sufficient searching, you have not found a paper that significantly overlaps with your idea.
Decide a paper idea is not novel, if you have found a paper that significantly overlaps with your idea.

{task_description}
"""

novelty_prompt = '''Round {current_round}/{num_rounds}.
You have this idea:

"""
{idea}
"""

The results of the last query are (empty on first round):
"""
{last_query_results}
"""

Respond in the following format:

THOUGHT:
<THOUGHT>

RESPONSE:
```json
<JSON>
```

In <THOUGHT>, first briefly reason over the idea and identify any query that could help you make your decision.
If you have made your decision, add "Decision made: novel." or "Decision made: not novel." to your thoughts.

In <JSON>, respond in JSON format with ONLY the following field:
- "Query": An optional search query to search the literature (e.g. attention is all you need). You must make a query if you have not decided this round.

A query will work best if you are able to recall the exact name of the paper you are looking for, or the authors.
This JSON will be automatically parsed, so ensure the format is precise.'''


def check_idea_novelty(
        ideas,
        rearch_topic,
        client,
        model,
        max_num_iterations=3,
):

    task_description = 'You are given the following file to work with. The rearch topic is: ' + rearch_topic


    for idx, idea in enumerate(ideas):
        if "novel" in idea:
            print(f"Skipping idea {idx}, already checked.")
            continue

        print(f"\nChecking novelty of idea {idx}: {idea['Name']}")

        novel = False
        msg_history = []
        papers_str = ""

        for j in range(max_num_iterations):
            try:
                text, msg_history = get_response_from_llm(
                    novelty_prompt.format(
                        current_round=j + 1,
                        num_rounds=max_num_iterations,
                        idea=idea,
                        last_query_results=papers_str,
                    ),
                    client=client,
                    model=model,
                    system_message=novelty_system_msg.format(
                        num_rounds=max_num_iterations,
                        task_description=task_description
                    ),
                    msg_history=msg_history,
                )
                time.sleep(1)
                if "decision made: novel" in text.lower():
                    print("Decision made: novel after round", j)
                    novel = True
                    break
                if "decision made: not novel" in text.lower():
                    print("Decision made: not novel after round", j)
                    break

                ## PARSE OUTPUT
                json_output = extract_json_between_markers(text)
                assert json_output is not None, "Failed to extract JSON from LLM output"

                ## SEARCH FOR PAPERS
                query = json_output["Query"]
                papers = search_for_papers(query, result_limit=10)
                if papers is None:
                    papers_str = "No papers found."

                paper_strings = []
                for i, paper in enumerate(papers):
                    paper_strings.append(
                        """{i}: {title}. {authors}. {venue}, {year}.\nNumber of citations: {cites}\nAbstract: {abstract}""".format(
                            i=i,
                            title=paper["title"],
                            authors=paper["authors"],
                            venue=paper["venue"],
                            year=paper["year"],
                            cites=paper["citationCount"],
                            abstract=paper["abstract"],
                        )
                    )
                papers_str = "\n\n".join(paper_strings)

            except Exception as e:
                print(f"Error: {e}")
                continue

        idea["novel"] = novel

    return ideas


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

def ensure_folder_exists(json_file_path):

    folder_path = os.path.dirname(json_file_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


if __name__ == "__main__":
    

    os.environ["GPT4o_KEY"] = ''

    os.environ["GPT4o_url"] = ''

    os.environ["S2_API_KEY"] = ''


    client, client_model = create_client('gpt-4o-2024-11-20')


    api_key_deepseek = ''
    base_url_kimi = ''
    base_url_deepseek = ''


    model_api = Deepseek([api_key_deepseek], base_url_deepseek)


#######################################################################################################################################



    find_cite_result_directory = "../target_paper_data.json"  #target_paper_data path


    with codecs.open(find_cite_result_directory, "r") as f:
        datasets = json.load(f)
        f.close()

    # example, you can change them depend on your need
    NUM_REFLECTIONS = 3
    num_ideas = 2



    first_ideas_save_path = '../model_output/AI-Scientist/first_ideas.json'  # model_output path
    second_ideas_save_path = '../model_output/AI-Scientist/second_ideas.json' # model_output path
    final_ideas_save_path = '../model_output/AI-Scientist/final_ideas.json' # model_output path


    cited_paper_conten_save_path = '../dataset_temple/cited_paper_conten.json' #dataset_temple path

    ensure_folder_exists(first_ideas_save_path)
    ensure_folder_exists(second_ideas_save_path)
    ensure_folder_exists(final_ideas_save_path)
    ensure_folder_exists(cited_paper_conten_save_path)



    with codecs.open(first_ideas_save_path, "r") as f:
        first_ideas_saves_ = json.load(f)
        f.close()

    first_ideas_saves = {}        
    for first_ideas_save in first_ideas_saves_:
        first_ideas_saves[first_ideas_save['index']] = first_ideas_save


    with codecs.open(second_ideas_save_path, "r") as f:
        second_ideas_saves_ = json.load(f)
        f.close()

    second_ideas_saves = {}        
    for second_ideas_save in second_ideas_saves_:
        second_ideas_saves[second_ideas_save['index']] = second_ideas_save



    for input_data in datasets:

        if input_data["summary"]["revised_topic"]:

            topic = input_data["summary"]["revised_topic"]
        
        else:

            topic = input_data["summary"]["topic"]


        cite_paper_id = 0
        all_paper_input = ''

        all_paper_conten = []
        for cites_paper in input_data["find_cite"]["top_references"]:

            paper_local_path = cites_paper['paper_local_path']

            cite_paper_conten = get_one_paper_conten(model_api, paper_local_path, topic)


            idea = cite_paper_conten['idea']
            experiment = cite_paper_conten['experiment']
            entities = cite_paper_conten['entities']

            one_paper_input = get_one_paper_input(cite_paper_id, idea, entities, experiment)



            all_paper_conten.append({"paper_path":paper_local_path,
                                    "model_result":one_paper_input})

            

            all_paper_input = all_paper_input + '\n' +one_paper_input
                    

        if data_check(cited_paper_conten_save_path, input_data['index']):
            pass
        else:
            append_to_json_file(cited_paper_conten_save_path, all_paper_conten, input_data['index'])


        if data_check(first_ideas_save_path, input_data['index']):
            ideas_first = first_ideas_saves[input_data['index']]['model_result']
            pass
        else:
            ideas_first = generate_ideas(
                all_paper_input,
                topic,
                client=client,
                model=client_model,
                max_num_generations=num_ideas,
                num_reflections=NUM_REFLECTIONS,
            )
            append_to_json_file(first_ideas_save_path, ideas_first, input_data['index'])


        if data_check(second_ideas_save_path, input_data['index']):
            print(input_data['index'])
            ideas_final = second_ideas_saves[input_data['index']]['model_result']
            pass
        else:
            ideas_final = check_idea_novelty(
                ideas_first,
                topic,
                client=client,
                model=client_model
            )

            append_to_json_file(second_ideas_save_path, ideas_final, input_data['index'])


        if data_check(final_ideas_save_path, input_data['index']):
            pass
        else:
            novel_ideas = [idea for idea in ideas_final if idea["novel"]]

            append_to_json_file(final_ideas_save_path, novel_ideas, input_data['index'])



