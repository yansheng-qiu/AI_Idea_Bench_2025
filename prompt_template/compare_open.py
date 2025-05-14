
def get_judge_ideas_all_prompt(idea0, idea1, topic):
    system_prompt = """
You are a judge in a competition. Your task is to evaluate and compare two ideas based on their motivation and experiment plans. You must decide which idea is better according to the evaluation criteria provided. Be objective, avoid biases, and ensure your decision is based solely on the quality of the ideas and experiments.
"""

    user_prompt = f"""
The motivation and experiment plan of idea0 is: {{{idea0}}}

The motivation and experiment plan of idea1 is: {{{idea1}}}

The topic of the competition is: {{{topic}}}

Which motivation and experiment do you think is better? Please write a short paragraph to explain your choice.

Here are your evaluation criteria:

1. Novelty: Are the problems or approaches new? Is this a novel combination of familiar techniques? Is it clear how this work differs from previous contributions? Is related work adequately referenced? 
2. Significance: Are the ideas important? Are other people (practitioners or researchers) likely to use these ideas or build on them? Does the idea address a difficult problem in a better way than previous research? Does it provide a unique theoretical or pragmatic approach?
3. Quality: Is there a clear rationale for each step of the experimental design? Are the baseline and evaluation metrics chosen appropriately? Has the design taken into account the potential advantages and limitations of the methods used? Can this experimental design effectively support the claims made in the idea.
4. Feasibility: Can the idea be realized with existing technology or methods? Are there any technical difficulties or bottlenecks? Is the idea clear and logical? Is there any obvious error or unreasonable part in the idea, and can the experiment be designed normally according to this idea. 
5. Clarity: Is the motivation and experiment clearly written? Does it provide enough information for the expert reader to understand the experiment? Is it well organized? Does it adequately inform the reader?
6. Relevance to Topic: Does the idea align with the provided topic? Does it address the core themes or issues raised by the topic? How closely is the idea tied to the overall focus of the competition?

Note: Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. DO NOT allow the LENGTH of the responses to influence your evaluation, choose the one that is straight-to-the-point instead of unnecessarily verbose. Be as objective as possible. (very important!!!)

If you think idea0 is better than idea1, you should output 0. If you think idea1 is better than idea0, you should output 1.

Your output should be strictly in the following JSON format:
{{
    "Novelty_choice": {{
        "thinking_process": "Your detailed reasoning here...",
        "choice": <Your choice (0 or 1)>
    }},
    "Significance_choice": {{
        "thinking_process": "Your detailed reasoning here...",
        "choice": <Your choice (0 or 1)>
    }},
    "Feasibility_choice": {{
        "thinking_process": "Your detailed reasoning here...",
        "choice": <Your choice (0 or 1)>
    }},
    "Clarity_choice": {{
        "thinking_process": "Your detailed reasoning here...",
        "choice": <Your choice (0 or 1)>
    }},
    "Relevance_choice": {{
        "thinking_process": "Your detailed reasoning here...",
        "choice": <Your choice (0 or 1)>
    }}

    "Final_choice": <Your choice (0 or 1)>
}}
"""

    return system_prompt, user_prompt





def split_motivation_experiment_plan(motivation_experiment_plan):
    system_prompt = f"""
    You are required to act as an AI annotator and extract the methods mentioned or implied in the motivation and experiment plan sections of the provided academic paper. The extraction should be done sentence by sentence, identifying any potential methods or techniques, whether explicitly stated or indirectly suggested.

    A "method" or "technique" refers to a specific approach, algorithm, procedure, tool, or strategy mentioned or implied in the text. For each method, extract the core **keywords** that best represent the technique or approach. If a specific name of a method is mentioned, replace it with relevant keywords related to the technique. If the method is implied but not directly named, infer the core **keywords** associated with the method based on the context.

    For each sentence, follow these guidelines:

    1. Identify the method(s) or technique(s) mentioned in the sentence.
    2. If a specific name is used for a method, replace it with **keywords** related to the technique (such as “neural network,” “classification,” “transfer learning,” etc.).
    3. If the method is implied but not directly named, infer the **keywords** that best describe the core functionality or application of the method.
    4. Each method should be represented by a set of **keywords** that capture the essence of the technique, without unnecessary details.
    5. Ensure that the **keywords** are distinct and representable in a simple form.

    """


    user_prompt = f"""
    Please extract the methods mentioned or implied in the motivation and experiment plan sections of the following academic paper. For each sentence, identify potential methods or techniques, whether explicitly stated or indirectly suggested.

    
    Your response should be in JSON format, structured as follows:

    {{
        "motivation": [
            {{
                "sentence": "<The sentence from the motivation section>",
                "methods": [
                    "<Keyword 1>",
                    "<Keyword 2>",
                    ...
                ]
            }},
            ...
        ],
        "experiment_plan": [
            {{
                "sentence": "<The sentence from the experiment plan section>",
                "methods": [
                    "<Keyword 1>",
                    "<Keyword 2>",
                    ...
                ]
            }},
            ...
        ]
    }}
    
    **Example**:

    **System's Input:**
    State-of-the-art computer vision systems are trained to predict a fixed set of predetermined object categories. To handle new categories, transfer learning techniques are employed to adapt the model to new data.

    **Your Answer (in JSON format):**
    {{
        "motivation": [
            {{
                "sentence": "State-of-the-art computer vision systems are trained to predict a fixed set of predetermined object categories.",
                "methods": [
                    "training",
                    "object classification",
                    "feature extraction"
                ]
            }}
        ],
        "experiment_plan": [
            {{
                "sentence": "To handle new categories, transfer learning techniques are employed to adapt the model to new data.",
                "methods": [
                    "transfer learning",
                    "model adaptation",
                    "domain adaptation"
                ]
            }}
        ]
    }}

    Motivation and experiment_plan:
    {motivation_experiment_plan}

    """

    return system_prompt, user_prompt







def create_experiment_evaluation_prompt(motivation, experiment_plan):
    system_prompt = """
You are tasked with evaluating an experiment plan to determine how well it addresses the problems identified in the motivation section. Your evaluation should include:

1. **Step-by-Step Evaluation:**  
   For each step in the experiment plan, assess how effectively it addresses the specific problems outlined in the motivation. Use the following scoring scale:

   - **1 (Poor):** The step does not address the problem, or the connection to the motivation is unclear.
   - **2 (Fair):** The step partially addresses the problem, but the solution is incomplete or weakly connected.
   - **3 (Good):** The step effectively addresses the problem, but the solution has minor gaps.
   - **4 (Very Good):** The step thoroughly addresses the problem with a well-structured solution.
   - **5 (Excellent):** The step comprehensively solves the problem, aligning closely with the motivation.

2. **Overall Evaluation:**  
   After evaluating each step, provide a final overall score for the experiment plan as a whole. Use the following scoring scale:

   - **1 (Poor):** The plan fails to address the motivation or solves very few of the identified problems.
   - **2 (Fair):** The plan addresses some problems but is incomplete or inconsistent.
   - **3 (Good):** The plan addresses most problems, but gaps exist in certain steps.
   - **4 (Very Good):** The plan addresses nearly all problems effectively, with clear and well-aligned steps.
   - **5 (Excellent):** The plan successfully addresses all problems with a clear, coherent structure.

Please output your evaluation in JSON format as follows:

```json
{
  "steps": [
    {
      "step_number": 1,
      "score": 4,
      "rationale": "The step addresses the problem clearly, with only minor gaps in the solution."
    },
    {
      "step_number": 2,
      "score": 3,
      "rationale": "The step partially addresses the problem but lacks a fully structured solution."
    }
    // Continue for each step...
  ],
  "overall_score": 4,
  "overall_rationale": "The plan addresses most problems effectively, though a few minor gaps remain."
}
"""
    user_prompt = f"""

Motivation:
"{motivation}"

Experiment Plan:
"{experiment_plan}"

For each step in the experiment plan, provide a score from 1 to 5 based on how effectively it addresses the problems mentioned in the motivation. After scoring each step, provide a final overall score for the entire experiment plan.
"""

    return system_prompt, user_prompt
