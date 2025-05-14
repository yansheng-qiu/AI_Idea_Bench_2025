
def get_one_paper_input(paper_id, idea, entities, experiment) -> str:
    prompt = f"""
Paper {paper_id}'s idea: {idea}

Paper {paper_id}'s experiment: {experiment}
"""
    return prompt





def get_deep_reference_prompt(paper_content: str,topic) -> str:
    prompt = f"""
You are a scientific research expert, tasked with extracting and summarizing information from provided paper content relevant to the topic: {topic}. Your deliverables will include pertinent references, extracted entities, a detailed summary, and the experimental design.

The topic you are studying is: {topic}. (Ensure that the references are pertinent to this topic.)

Extraction Requirements:
Entities
1. Identify unique entities mentioned in the paper, such as model names, datasets, metrics, and specialized terminology.
2. Format the entities with a name followed by a brief description.
3. Ensure all entities are relevant to the specified topic ([topic]).


Summary Idea:
1. Background: Elaborate on the task's context and previous work, outlining the starting point of this paper.
2. Novelty: Describe the main innovations and contributions of this paper in comparison to prior work.
3. Contribution: Explain the primary methods used, detailing the theory and functions of each core component.
4. Detail Reason: Provide a thorough explanation of why the chosen methods are effective, including implementation details for further research.
5. Limitation: Discuss current shortcomings of the approach.

Experimental Content:
1. Experimental Process: Detail the entire experimental procedure, from dataset construction to specific steps, ensuring clarity and thoroughness.
2. Technical Details: Describe any specific technologies involved, providing detailed implementation processes.
3. Clarity of Plan: State your experimental plan concisely to facilitate understanding without unnecessary complexity.
4. Baseline: Elaborate on the baseline used, comparative methods, and experimental design, illustrating how these support and validate the conclusions drawn.
5. Verification: Explain how your experimental design assists in verifying the core idea and ensure it is detailed and feasible.

Relevance Criteria:
1. Method Relevance: References must directly correlate with the paper's methodology, indicating improvements or modifications.
2. Task Relevance: References should address the same task, even if methods differ, better have the same topic {topic}.
3. Baseline Relevance: References should serve as baselines for the methods discussed in the paper.
4. Output Format: Provide references without author names or publication years, formatted as titles only.
5. Specific paper titles will be placed between <References></References>. Based on the precise citation location and the corresponding ref_id in the paper, you need to infer the specific title of your output relevant references.


The paper content is as follows: 
{paper_content}


Please provide the entities, summary idea, experimental design, and the three most relevant references (Sort by relevance, with priority given to new ones with the same level of relevance, do not reference the original paper.) based on the paper's content.
Note: Ensure the references are pertinent to the topic you are studying: {topic}. If there are no relevant references, output <references>[]</references>.

Now please output strictly in the following format:
<entities>{{A list of entities you extract}}</entities>
<idea>{{Background: ... \nNovelty: ...\nContribution:...\nMethods:...\nDetail reason:...\nLimitation:...\n }}</idea>
<experiment>{{Step1:... Step2:...}}</experiment>
<references>["{{Title1}}", "{{Title2}}",  ...]</references>
"""
    return prompt






def find_most_cite_paper():
    system_prompt = f"""
You are an academic assistant tasked with analyzing a research paper and identifying the top most-cited references within it. For each reference, provide the title, the cited number, and the sections where the reference is cited, along with the cited number in each section.
    """
    
    json_template = {
        "top_references": [
            {
                "rank": 1,
                "title": "A Comprehensive Study on Machine Learning Techniques",
                "cited_number": 5,
                "sections": [
                    {"name": "Introduction", "cited_number": 3},
                    {"name": "Literature Review", "cited_number": 2}
                ]
            },
            {
                "rank": 2,
                "title": "Deep Learning for Natural Language Processing",
                "cited_number": 5,
                "sections": [
                    {"name": "Methodology", "cited_number": 3},
                    {"name": "Results", "cited_number": 2}
                ]
            },
            {
                "rank": 3,
                "title": "Neural Networks and Their Applications",
                "cited_number": 4,
                "sections": [
                    {"name": "Literature Review", "cited_number": 2},
                    {"name": "Discussion", "cited_number": 2}
                ]
            },
            {
                "rank": 4,
                "title": "Understanding AI Algorithms in Modern Computing",
                "cited_number": 4,
                "sections": [
                    {"name": "Introduction", "cited_number": 3},
                    {"name": "Conclusion", "cited_number": 1}
                ]
            },
            {
                "rank": 5,
                "title": "Advances in Supervised Learning",
                "cited_number": 3,
                "sections": [
                    {"name": "Methodology", "cited_number": 3}
                ]
            },
            {
                "rank": 6,
                "title": "Applications of AI in Healthcare",
                "cited_number": 3,
                "sections": [
                    {"name": "Literature Review", "cited_number": 2},
                    {"name": "Discussion", "cited_number": 1}
                ]
            },
            {
                "rank": 7,
                "title": "A Survey of Reinforcement Learning Techniques",
                "cited_number": 2,
                "sections": [
                    {"name": "Introduction", "cited_number": 2}
                ]
            },
            {
                "rank": 8,
                "title": "The Evolution of Neural Network Models",
                "cited_number": 2,
                "sections": [
                    {"name": "Methodology", "cited_number": 2}
                ]
            },
            {
                "rank": 9,
                "title": "Optimization Methods in Machine Learning",
                "cited_number": 2,
                "sections": [
                    {"name": "Literature Review", "cited_number": 1},
                    {"name": "Results", "cited_number": 1}
                ]
            },
            {
                "rank": 10,
                "title": "Data Mining and Its Challenges",
                "cited_number": 1,
                "sections": [
                    {"name": "Conclusion", "cited_number": 1}
                ]
            }
        ]
    }


    prompt = f"""

Please follow the following steps for analysis:
1. Read the entire thesis carefully and count the number of citations for each reference.
2. Identify the top ten references with the highest number of citations.
3. For each selected reference, determine its title, the total number of citations, as well as the chapters in which it is cited and the number of citations in each chapter.
4. Output the results in the following JSON structure in descending order of the number of citations: 


Use the following JSON structure for the output:
{json_template}
"""
    
    return prompt, system_prompt

def find_motivation_paper():

  system_prompt = f"""
You are an academic assistant tasked with extracting relevant sentences and references from the Introduction and Method sections of a paper.
    """
  json_template = {
"paper_title": "Paper Title Here",
"motivation": [
    {
    "sentence": "This method is motivated by the approach presented in [Reference 1], [Reference 2].",
    "references": [
        "Reference 1 Paper Title",
        "Reference 2 Paper Title"
    ],
    "section": 'Introduction'
    },
        {
    "sentence": "This method is motivated by the approach presented in [Reference 1], [Reference 2].",
    "references": [
        "Reference 1 Paper Title",
        "Reference 2 Paper Title"
    ],
    "section": 'Method'
    }
]
}
  prompt = f"""
Please read the introduction and method section of the following paper thoroughly and extract the sections where the paper explicitly states 'following', 'motivated by', or 'inspired by'. For each instance of these phrases, provide the exact sentence(s) and list all the referenced papers being cited. If there are multiple references for a single sentence, list them all by providing the following details in JSON format:. If no such sentences are found, return an empty result.

Format the output in a standardized JSON structure with the following keys:

- 'paper_title': The title of the current paper you are analyzing.
  - 'sentence': The exact sentence where the paper cites references using 'following', 'motivated by', or 'inspired by'.
  - 'references': An array of strings, each being the full title of a referenced paper mentioned in the sentence.
  - 'section': Where the exact sentence is located.

Ensure that only the paper titles, the sentence and the location of the sectence are included and in the output, and omit any extraneous details. The sectences only locat at the Introduction and Method sections.
If no references in this sentence, don't show in the result.

Use the following JSON structure for the output:
{json_template}

"""
  return prompt, system_prompt


def summary_paper():
    

  system_prompt = f"""
You are an AI assistant tasked with summarizing research papers in a structured and clear manner.
    """
    
    
  json_template = {
  "topic": "The main research object and scope of the study",
  "motivation": "Current state of the field, achievements, and limitations addressed by this study",
  "method": {
    "targeted_designs_summary": "A high-level summary of the designs or innovations made to address limitations",
    "targeted_designs_details": [
      {
        "design_name": "Name of the design",
        "description": "Detailed explanation of this design, including its purpose, how it addresses limitations, and any novel aspects (anonymized)",
        "problems_solved": "Problem that this design solve"
      },
      {
        "design_name": "Name of another design",
        "description": "Detailed explanation of this design (anonymized)",
        "problems_solved": "Problem that this design solve"
      }
    ],
    "datasets": "Datasets used in the experiments",
    "metrics": "Evaluation metrics used to assess the effectiveness of the approach"
  }
}
    
  prompt = f"""
Please summarize the following research paper by providing the following details in JSON format:

1. Topic: Identify the key concepts, research questions, or objectives discussed in the paper. Summarize the main topic in one or two sentences, ensuring it captures the essence of the paper. Avoid including unnecessary details or examples.

2. Motivation: Provide an explanation of the current state of the field. What are the key achievements in this area of research, and what are the limitations or open challenges that this paper addresses? Describe why this research is important and how it aims to contribute to advancing the field.

3. Method: Explain the methodology used in the paper. In particular, describe the specific designs or approaches the authors implemented to address the limitations or gaps identified in the motivation. Provide a summary of the targeted designs, followed by a detailed explanation of each design individually. 

- Summary: Give an overview of the key innovations or design choices made to overcome existing limitations in the field.
- Detailed designs: For each targeted design, provide a thorough explanation. Discuss innovations in model architecture, algorithms, data processing techniques, or training strategies. Please anonymize the names of the methods in the descriptions.
- Problems solved: List the specific problems that each design addresses, separately.
- Datasets: Mention the datasets used for training and testing the model, including any unique characteristics or challenges they present.
- Metrics: Specify the evaluation metrics used to assess the model's performance, such as accuracy, precision, recall, F1 score, etc.

Requirements:
- Provide clear and concise explanations.
- Summarize the content in a structured, easy-to-read format.
- For the "Method" section, ensure that:
  - Targeted designs: The summary should provide an overview of the key innovations or strategies.
  - Individual designs: Determine what small designs make up the overall framework, break down the whole framework into individual small design and use the orignal sentece from the paper to explain them in detail separately, such as the detail architectural changes, novel algorithms, or new techniques. Anonymize the names of methods and techniques by describing them in a general sense, avoiding any specific names.
  - Problems solved: List the specific problems each design addresses separately
  - Datasets: Mention the datasets used for training and testing the model, including any unique characteristics or challenges they present.
  - Metrics: Specify the evaluation metrics used to assess the model's performance, such as accuracy, precision, recall, F1 score, etc.

- Use the following JSON structure for the output:

{json_template}

Here is the provided paper:
"""
  return prompt, system_prompt






def refine_topic(topic, motivation):
    system_prompt = f"""
You are an expert in academic writing and text analysis. Your task is to evaluate whether a given topic statement is concise, specific, and focused on the core theme. The topic should avoid unnecessary details or examples that don’t directly contribute to the core concept. Your goal is to remove unnecessary content, leaving just the essential theme.

Provide your output in JSON format, following the instructions precisely.
    """
    
    json_template_output = {
        "original_topic": "The paper introduces a novel Part Re-projection Distance Loss (PRDL) for 3D face reconstruction, leveraging facial part segmentation to improve alignment and reconstruction accuracy, especially for extreme expressions.",
        "contains_unnecessary_details": True,
        "revised_topic": "The topic of this paper is 3D face reconstruction."
    }
    
    prompt = f"""
1. Carefully read the provided topic statement and motivation.
2. Assess if the statement contains unnecessary details, such as specific methods, examples, or tangential content. Focus on identifying any overly specific explanations that don't contribute to the core subject.
3. If unnecessary details are found, suggest a revised version of the topic that keeps only the main subject, removing extraneous content. The revised version should follow the format: "The topic of this paper is [revised topic]."
4. If no unnecessary details are found, confirm that the topic is concise and specific.
5. Format your output as a JSON object with the following keys:
   - original_topic: The original topic statement provided.
   - contains_unnecessary_details: A boolean value (true or false) indicating whether unnecessary details or examples are present.
   - revised_topic: If unnecessary details are found, provide a revised version of the topic statement in the format "The topic of this paper is [revised topic]." If no unnecessary details are found, set this to null.

**Example Input:**
"The paper introduces a novel Part Re-projection Distance Loss (PRDL) for 3D face reconstruction, leveraging facial part segmentation to improve alignment and reconstruction accuracy, especially for extreme expressions."

**Example Output:**
{json_template_output}


Here is a motivation for reference:
{motivation}

**Now, evaluate the following topic statement:**
{topic}
"""
    return prompt, system_prompt



def create_keyword_extraction_prompt(topic):
    system_prompt = f"""
You are an assistant specializing in extracting key, relevant keywords from a provided topic. Your goal is to identify specific keywords that directly represent the corefocus of the text. These keywords should be clear, precise, and directly linked to the topic's content. Avoid using broad, vague, or overly general terms.

Instructions:
1. Carefully read the provided topic to fully understand its core focus.
2. Extract specific, important keywords that are closely tied to the core themes, concepts, or findings of the topic. These keywords should be essential to understanding the subject matter.
3. Rank the extracted keywords by relevance, starting with the most important.
4. For each keyword, provide a concise explanation that justifies its ranking and details how it connects to the main focus of the topic.
5. The output should be in JSON format with each keyword and its explanation as a dictionary object.
    """


    json_template_output ={
    "keywords": [
        {
            "rank": 1,
            "keyword": "Keyword 1",
            "explanation": "Explanation of why this keyword is the most relevant."
        },
        {
            "rank": 2,
            "keyword": "Keyword 2",
            "explanation": "Explanation of why this keyword is the second relevant."
        },
        ...
    ]
}

    user_prompt = f"""
**Input:**
- Topic: {topic}

**Output:**
- "rank": The position of the keyword based on its relevance, with 1 being the most important.
- "keyword": The specific keyword that represents a key concept related to the topic.
- "explanation": A short justification for why this keyword is central to the topic.

**Output Format:**
- The output should be in JSON format with the following structure:

{json_template_output}
    """

    return system_prompt, user_prompt