<h1 align="center">
  <b>AI Idea Bench 2025: AI Research Idea Generation Benchmark</b><br>
</h1>

<p align="center">
  📚 <a href="https://arxiv.org/pdf/2504.14191">[Paper]</a>
  🤗 <a href="https://huggingface.co/datasets/yanshengqiu/AI_Idea_Bench_2025">[Dataset]</a>
</p>


## 💬 Introduction

### Benchmark
We construct the AI Idea Bench 2025 dataset, comprising 3,495 influential target papers in AI-related conferences along with their corresponding motivating papers, to systematically evaluate the effectiveness of idea generation methods.
### Evaluation Framework
We propose an evaluation framework that aligns generated research ideas with the content of ground-truth papers, while simultaneously assessing their merits and drawbacks based on other reference material.


## 🚀 Pipline

### Data preparation

Download the data from <a href="https://huggingface.co/datasets/yanshengqiu/AI_Idea_Bench_2025">[Huggingface]</a> and then get the path to the data,

```bash
your_papers_data_path = '/papers_data/'
target_paper_data = '/target_paper_data.json'
```
and change the './papers_data/' in target_paper_data.json by your_papers_data_path

My project code framework for reference
```
Idea_bench_data/
├── code (current repository)
├── papers_data   
├── target_paper_data.json

```

### Preparation for SciPDF Parser:
Install [SciPDF Parser](https://github.com/titipata/scipdf_parser) for PDF parsing.
```bash
git clone https://github.com/titipata/scipdf_parser.git
pip install git+https://github.com/titipata/scipdf_parser
python -m spacy download en_core_web_sm
```

### Preparation for grobid:
Install java for grobid
```bash
wget  https://download.oracle.com/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar -zxvf openjdk-11.0.2_linux-x64_bin.tar.gz
export JAVA_HOME=Your_path/jdk-11.0.2
```

### Run grobid

If you can successfully start grobid in [SciPDF Parser](https://github.com/titipata/scipdf_parser.git), run the following commands:
```bash
cd scipdf_parser
bash serve_grobid.sh
```

(Optional) Or, you can refer to the following process to install grobid if the previous commands fail:
```bash
git clone https://github.com/kermitt2/grobid.git
cd grobid
./gradlew clean install
./gradlew run
```

### Generate ideas

Set your dataset_temple path in extract_one_paper_conten.py lines 10



```bash
cd ./AI-Scientist
```

Set your code paths, semantic scholar API, GPT-4o API, deepseek API, output file paths in generate_ideas_fron_papers.py lines 16, 472-476, 482-484, 494, and 507-512.


```bash
python generate_ideas_fron_papers.py

cd ..
```


### Idea multiple-choice evaluation
Set cited_paper_conten path, target_paper_data path,output file paths in Make_MCQ.py lines 51,74,98,128 and 205




```bash
python Make_MCQ.py # Make mcq questions
```

Set your deepseek api in MCQ.py lines 22-26

```bash
python MCQ.py
```


### Idea to idea matching

Set your deepseek api in idea_gt_idea.py lines 54-57

```bash
python idea_gt_idea.py
```

### Idea to idea matching

Set your deepseek api in idea_gt_topic.py lines 54-57

```bash
python idea_gt_topic.py
```

### Ideas competition among baselines

Set your deepseek api in competition.py lines 288-292

```bash
python competition.py
```


### Novelty assessment

Set semantic scholar API in find_paper_by_kewords.py lines 16

```bash
python find_paper_by_kewords.py  # Find curren papers and history papers
```

Set your deepseek api in extract_hd_cd_paper.py lines 96-98
```bash
python extract_hd_cd_paper.py
```
**Attention !!** There will be a failure to parse papers here, this is because some papers cannot be downloaded via the script. For this problem, we are manually to download again.


Set your deepseek api in Novelty.py lines 288-292

```bash
python Novelty.py
```

### Feasibility

Set your deepseek api in split_experimental_plan.py lines 62-64

```bash
python split_experimental_plan.py  # split experimental plan of generated ideas
```



### Novelty assessment

Set semantic scholar API in feasibility.py lines 12

```bash
python feasibility.py 
```

## 🚩 License
This repository is under the Apache-2.0 license. For commercial use, please contact with the authors.


## 📜 Citations
```
@article{qiu2025ai,
  title={AI Idea Bench 2025: AI Research Idea Generation Benchmark},
  author={Qiu, Yansheng and Zhang, Haoquan and Xu, Zhaopan and Li, Ming and Song, Diping and Wang, Zheng and Zhang, Kaipeng},
  journal={arXiv preprint arXiv:2504.14191},
  year={2025}
}
```
## 🔈 Acknowledgements
This repository is based on the following Github repositories. Thanks to the following public repositories:
- [AI-Scientist](https://github.com/SakanaAI/AI-Scientist)
- [CoI-Agent](https://github.com/DAMO-NLP-SG/CoI-Agent)

**Note:** This is a research level repository and might contain issues/bugs. Please contact the authors for any query.