import json

def compare_motivation(input_motivation, option_a, option_b, option_c, option_d):

    system_prompt = """
You are an AI motivation analyzer. Your task is to compare a user-provided motivation against four options (A, B, C, D) and identify the closest match. Follow these steps:  
1. **Analyze the Input**: Extract the core problem, theme, or goal from the input motivation.  
2. **Compare Options**: Evaluate each option (A-D) by identifying its primary focus (problem addressed, underlying theme, or end goal).  
3. **Match Criteria**: Prioritize matches based on shared intent, not just keywords. Discard superficial similarities.  
4. **Explain Clearly**: Highlight specific overlapping elements (e.g., "both target efficiency improvement" or "address ethical concerns").  
    """
    user_prompt = f"""
Return a JSON response with:  
- `closest_option`: The best-matched option (A-D).  
- `explanation`: A concise, evidence-based comparison (1-2 sentences).  

**Input Motivation:** {input_motivation}
"**Options:**
- A: {option_a}
- B: {option_b}
- C: {option_c}
- D: {option_d}
Provide your response in JSON format as follows:
{{  
  "closest_option": "A",  
  "explanation": "[Input motivation] aligns with Option A because both [specific shared problem/theme/goal]. For example, [concrete similarity]."  
}}  
    """
    return system_prompt, user_prompt






def compare_plan(input_plan, plan_a, plan_b, plan_c, plan_d):
    # System Prompt
    system_prompt = """
You are an expert in comparative analysis of scientific methodologies. Your task is to match an input experiment plan to the most similar of four predefined plans (A, B, C, D) by evaluating theoretical alignment and problem-solving focus.

**Analysis Guidelines**  
1. **Ignore**:  
   - Step order and step names.  
   - Superficial differences in terminology.  

2. **Compare using these criteria**:  
   - **Structural & Theoretical Alignment**: Core framework, methodology organization, and foundational principles.  
   - **Problem Focus**: Type of challenges addressed, objectives prioritized, and domain-specific issues targeted.  

3. **Output Requirements**:  
   - Return JSON with two keys: `closest_plan` (A-D) and `explanation` (3-5 sentences).  
   - In the explanation, explicitly address both structural/theoretical alignment **and** problem focus.  
    """

    # User Prompt
    user_prompt = f"""
Analyze this input experiment plan:  
`{input_plan}`  

Compare it against these predefined plans:  
- **A**: {plan_a}  
- **B**: {plan_b}  
- **C**: {plan_c}  
- **D**: {plan_d}  

Provide your analysis in JSON format.

**Expected Output Format:**

{{
  "closest_plan": "C",
  "explanation": "The input plan {input_plan} aligns with Plan C structurally through... Simultaneously, both address... [Always mention BOTH criteria]"
}}
    """


    return system_prompt, user_prompt



















def similarity_motivation_w_motivation(motivation1, motivation2):
    system_prompt = """
You are an AI trained to rigorously evaluate the similarity between two research motivations by analyzing their **structural alignment**, **theoretical foundations**, and **problem focus**. Your task is to compare each pair of motivations and determine how closely they address the same core issues, challenges, or research gaps. Prioritize depth of analysis over superficial keyword matching.
     """

    user_prompt = f"""
For each pair of motivations provided:  
1. **Analyze Core Issues**: Identify the central problem(s), challenge(s), or knowledge gap(s) each motivation emphasizes.  
2. **Compare Contextual Alignment**: Assess whether the motivations operate within the same domain, theoretical framework, or practical context.  
3. **Evaluate Structural/Theoretical Overlap**: Determine if they share methodologies, hypotheses, or foundational theories (even if applied differently).  

**Rating Criteria**:  
Rate similarity on a scale of 1–5:  
1. **No Similarity**: Entirely distinct problems, contexts, and methodologies.  
2. **Low Similarity**: Minimal overlap in one aspect (e.g., tangential problem mention but divergent focus/theory).  
3. **Moderate Similarity**: Shared problem domain but differing approaches/theories (e.g., both address climate change mitigation but focus on policy vs. technology).  
4. **High Similarity**: Aligned problem focus and theory with minor differences in scope or application (e.g., both study AI bias in healthcare, but one targets diagnostics and the other patient data).  
5. **Complete Similarity**: Identical problems, theories, and contextual applications.  

**Output Format**  
Return a JSON object for each pair with:  
- A numeric `rating` (1–5)  
- A concise `explanation` highlighting **specific overlaps** and **key distinctions** (1–2 sentences).  

**Example Output**:  
{{
  "motivation_similarity": {{
    "rating": 4,
    "explanation": "Both motivations address algorithmic bias in healthcare AI, but Motivation A focuses on diagnostic inaccuracies in radiology, while Motivation B emphasizes biases in patient prioritization systems."
  }}
}}

**Here are the motivations:**
    - Motivation 1: {motivation1}
    - Motivation 2: {motivation2}

    """

    return system_prompt, user_prompt





def similarity_experiment_plan_w_experiment_plan(experiment_plan1, experiment_plan2):
    system_prompt = """
You are an AI trained to evaluate the similarity between two experiment plans based on their structural design, theoretical foundations, and core problem focus. Ignore superficial differences like step order, naming conventions, or formatting details.
    """



    user_prompt = f"""
Compare the two provided experiment plans and assess their similarity using the criteria below.  

**Evaluation Criteria:**  
1. **Structural Similarity:**  
   - Do the plans share a comparable framework (e.g., hypothesis testing, control groups, data analysis methods)?  
   - Ignore differences in step order or terminology.  

2. **Theoretical Alignment:**  
   - Do they rely on the same or related theories, principles, or methodologies?  

3. **Problem Focus:**  
   - Do they address the same underlying problem or challenge, even if solutions differ?  


**Rating Scale (1–5):**  
1. **No similarity:** Entirely different problems/theories/structures.  
2. **Low similarity:** Minor overlap in one criterion (e.g., same problem but divergent theories).  
3. **Moderate similarity:** Align in 1–2 criteria with clear differences (e.g., shared theory but distinct structures).  
4. **High similarity:** Align in 2–3 criteria with minor discrepancies (e.g., same problem and structure but different theories).  
5. **Complete similarity:** Identical in all criteria.  


**Output Requirements:**  
- Return JSON format with `rating` (1–5) and `explanation`.  
- The explanation must explicitly reference **structure**, **theory**, and **problem focus**.  

**Example Output:**  

{{
  "experiment_plan_similarity": {{
    "rating": 3,
    "explanation": "Both address energy efficiency (problem focus) and use quantitative metrics (structure), but Plan 1 employs machine learning (theory) while Plan 2 uses statistical modeling (theory)."
  }}
}}

**Here are the Experiment Plans:**
- Experiment Plan 1: {experiment_plan1}
- Experiment Plan 2: {experiment_plan2}

    """

    return system_prompt, user_prompt











def generate_alignment_evaluation_prompts(topic, motivation, experiment_plan):
    # Define the system prompt
    system_prompt = """
    You are a highly advanced AI tasked with evaluating research papers. When asked to evaluate the alignment between the motivation and experiment plan with the topic of the paper, follow these guidelines:

    - Motivation: Check if the rationale clearly explains why this topic is being explored and how it connects to the broader context of the field. Identify the research gap or problem being addressed and ensure that it directly connects with the topic.
    - Experiment Plan: Assess whether the experiment design is directly aligned with the motivation. Determine if the methods proposed are appropriate for addressing the research questions identified in the motivation and if they suit the topic under investigation.

    After evaluating, assign a compatibility score (1-5) based on the following scoring rubric:
    """
    
    # Define the user prompt
    user_prompt = f"""
    Given the research paper's topic, evaluate whether the motivation and experiment plan are aligned with the focus of the study. Provide a compatibility score from 1 to 5, where:
    - 1 (Very Poor Alignment): The motivation and/or experiment plan are completely unrelated to the topic. The motivation does not address the topic, and the experiment plan does not effectively test the research question posed.
    - 2 (Poor Alignment): The motivation and/or experiment plan are weakly connected to the topic. The motivation addresses the topic but in a vague or unclear manner, and the experiment plan partially, but not effectively, tests the research question.
    - 3 (Moderate Alignment): The motivation and experiment plan are somewhat aligned with the topic. The motivation explains the topic, but with some gaps in clarity, and the experiment plan mostly addresses the research question, though some methods may not be optimal.
    - 4 (Good Alignment): The motivation and experiment plan are clearly aligned with the topic. The motivation explains the research problem well, and the experiment plan is suitable and addresses the research question effectively.
    - 5 (Excellent Alignment): The motivation and experiment plan are perfectly aligned with the topic. The motivation provides a strong, clear rationale for the study, and the experiment plan is highly suitable and directly addresses the research question in a methodologically sound way.

    Input:
    Topic: {topic} Motivation: {motivation} Experiment Plan: {experiment_plan}
    Please output your evaluation in JSON format with the following structure:

    {{
      "motivation": {{
        "alignment": <score (1-5)>,
        "comments": "<concise evaluation of motivation's alignment with topic>"
      }},
      "experiment_plan": {{
        "alignment": <score (1-5)>,
        "comments": "<concise evaluation of experiment plan's alignment with topic>"
      }}
    }}


    Ensure the output contains the specific evaluations for the motivation, experiment plan, and an overall compatibility score.



    """

    return system_prompt, user_prompt





