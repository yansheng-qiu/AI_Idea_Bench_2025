import requests
import scipdf
import os
import aiohttp
import asyncio
import numpy as np
import random
import codecs
import json

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


def extract(text, type):
    if text:
        target_str = get_content_between_a_b(f"<{type}>", f"</{type}>", text)
        if target_str:
            return target_str
        else:
            return text
    else:
        return ""


async def fetch(url):
    try:
        timeout = aiohttp.ClientTimeout(total=120)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.88 Safari/537.36'
        }  # Mimic a common browser's User-Agent
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.read()
                    return content
                else:
                    print(f"Failed to fetch the URL: {url} with status code: {response.status}")
                    return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching the URL: {url}", e)
        return None

    
class Result:
    def __init__(self,title="",abstract="",article=None,citations_conut = 0,year = None) -> None:
        self.title = title
        self.abstract = abstract
        self.article = article
        self.citations_conut = citations_conut
        self.year = year

def process_fields(fields):
   return ",".join(fields)


class SementicSearcher:
    def __init__(self, save_file = "papers/",ban_paper = []) -> None:
        self.save_file = save_file
        self.ban_paper = ban_paper
    
    async def search_papers_async(self, query, limit=5, offset=0, fields=["title", "paperId", "abstract", "isOpenAccess", 'openAccessPdf', "year","publicationDate","citations.title","citations.abstract","citations.isOpenAccess","citations.openAccessPdf","citations.citationCount","citationCount","citations.year"],
                            publicationDate=None, minCitationCount=0, year=None, 
                            publicationTypes=None, fieldsOfStudy=None):
        url = 'https://api.semanticscholar.org/graph/v1/paper/search'
        fields = process_fields(fields) if isinstance(fields, list) else fields
        
        # More specific query parameter
        query_params = {
            'query': query,
            "limit": limit,
            "offset": offset,
            'fields': fields,
            'publicationDateOrYear': publicationDate,
            'minCitationCount': minCitationCount,
            'year': year,
            'publicationTypes': publicationTypes,
            'fieldsOfStudy': fieldsOfStudy
        }
        await asyncio.sleep(0.5)
        try:
            filtered_query_params = {key: value for key, value in query_params.items() if value is not None}
            # Load the API key from the configuration file
            api_key = os.environ.get("SEMENTIC_SEARCH_API_KEY", None)
            headers = {'x-api-key': api_key} if api_key else None
            response = requests.get(url, params=filtered_query_params, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                await asyncio.sleep(5)  
                return response_data
            elif response.status_code == 429:
                await asyncio.sleep(5)  
                print(f"Request failed with status code {response.status_code}: begin to retry")
                return await self.search_papers_async(query, limit, offset, fields, publicationDate, minCitationCount, year, publicationTypes, fieldsOfStudy)
            else:
                await asyncio.sleep(5)  
                print(f"Request failed with status code {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
                
    def cal_cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def cal_cosine_similarity_matric(self,matric1, matric2):
        if isinstance(matric1, list):
            matric1 = np.array(matric1)
        if isinstance(matric2, list):
            matric2 = np.array(matric2)
        if len(matric1.shape) == 1:
            matric1 = matric1.reshape(1, -1)
        if len(matric2.shape) == 1:
            matric2 = matric2.reshape(1, -1)
        dot_product = np.dot(matric1, matric2.T)
        norm1 = np.linalg.norm(matric1, axis=1)
        norm2 = np.linalg.norm(matric2, axis=1)

        cos_sim = dot_product / np.outer(norm1, norm2)
        scores = cos_sim.flatten()
        return scores.tolist()
    
    def rerank_papers(self, query_embedding, paper_list,llm):
        if len(paper_list) == 0:
            return []
        paper_list = [paper for paper in paper_list if paper]
        paper_contents = []
        for paper in paper_list:
            paper_content = f"""
Title: {paper['title']}
Abstract: {paper['abstract']}
"""
            paper_contents.append(paper_content)
        paper_contents_embbeding = llm.get_embbeding(paper_contents)
        paper_contents_embbeding = np.array(paper_contents_embbeding)
        scores = self.cal_cosine_similarity_matric(query_embedding,paper_contents_embbeding)
            
        # 根据score对paper_list进行排序 
        paper_list = sorted(zip(paper_list,scores),key = lambda x: x[1],reverse = True)
        paper_list = [paper[0] for paper in paper_list]
        return paper_list
        
    
    async def search_async(self,query,max_results = 5 ,paper_list = None ,rerank_query = None,llm = None,year = None,publicationDate = None,need_download = True,fields = ["title", "paperId", "abstract", "isOpenAccess", 'openAccessPdf', "year","publicationDate","citationCount"]):
        
        # Read the papers that have been read
        readed_papers = []
        if paper_list:
            if isinstance(paper_list,set):
                paper_list = list(paper_list)
            if len(paper_list) == 0 :
                pass
            elif isinstance(paper_list[0], str):
                readed_papers = paper_list
            elif isinstance(paper_list[0], Result):
                readed_papers = [paper.title for paper in paper_list]

        print(f"Searching for papers related to query : <{query}>")
        results = await self.search_papers_async(query,limit = 6 * max_results,year=year,publicationDate = publicationDate,fields = fields)
        if not results or "data" not in results:
            return []
        
        # Remove the papers that have been read
        new_results = []
        for result in results['data']:
            if result['title'] in self.ban_paper:
                continue
            new_results.append(result)
        results = new_results

        if need_download:
            paper_candidates = []
            for result in results:
                if os.path.exists(os.path.join(self.save_file, f"{result['title']}.pdf")) and result['title'] not in readed_papers:
                    paper_candidates.append(result)
                elif not result['isOpenAccess'] or  not result['openAccessPdf']:
                    continue
                else:
                    paper_candidates.append(result)
        else:
            paper_candidates = results
        
        if llm and rerank_query:
            rerank_query_embbeding = llm.get_embbeding(rerank_query)
            rerank_query_embbeding = np.array(rerank_query_embbeding)
            paper_candidates = self.rerank_papers(rerank_query_embbeding, paper_candidates,llm)
        
        final_results = []
        for result in paper_candidates:
            article = None
            if need_download:
                if os.path.exists(os.path.join(self.save_file, f"{result['title']}.pdf")):
                    article = self.read_arxiv_from_path(os.path.join(self.save_file, f"{result['title']}.pdf"))
                else:
                    pdf_link = result['openAccessPdf']["url"]
                    article = await self.read_arxiv_from_link_async(pdf_link, f"{result['title']}.pdf")
                if not article:
                    continue
            title,abstract,citationCount,year = result["title"],result["abstract"],result["citationCount"],result["year"]
            final_results.append(Result(title,abstract,article,citationCount,year))
            if len(final_results) >= max_results:
                break
        return final_results

    async def search_related_paper_async(self,title,need_citation = True,need_reference = True,rerank_query = None,llm = None,paper_list = []):
        print(f"Searching for related papers of paper <{title}>; Citation:{need_citation}; Reference:{need_reference}")
        fileds = ["title","abstract","citations.title","citations.abstract","citations.citationCount","references.title","references.abstract","references.citationCount","citations.isOpenAccess","citations.openAccessPdf","references.isOpenAccess","references.openAccessPdf","citations.year","references.year"]
        results = await self.search_papers_async(title,limit = 3,fields=fileds)
        related_papers = []
        related_papers_title = []
        if not results or "data" not in results:
            print(f"Failed to find related papers of paper <{title}>; Citation:{need_citation}; Reference:{need_reference}")
            return None
        for result in results["data"]:
            if not result:
                continue
            if need_citation:
                for citation in result["citations"]:
                    if os.path.exists(os.path.join(self.save_file, f"{citation['title']}.pdf")) and citation["title"] not in paper_list:
                        if "openAccessPdf" not in citation or not citation["openAccessPdf"] or "url" not in citation["openAccessPdf"]:
                            citation["openAccessPdf"] = {"url":None}
                        related_papers.append(citation)
                        related_papers_title.append(citation["title"])
                    elif citation["title"] in related_papers_title or citation["title"] in self.ban_paper or citation["title"] in paper_list:
                        continue
                    elif citation["isOpenAccess"] == False or citation["openAccessPdf"] == None:
                        continue
                    else:
                        related_papers.append(citation)
                        related_papers_title.append(citation["title"])
            if need_reference:
                for reference in result["references"]:
                    if os.path.exists(os.path.join(self.save_file, f"{reference['title']}.pdf")) and reference["title"] not in paper_list:
                        if "openAccessPdf" not in reference or not reference["openAccessPdf"] or "url" not in reference["openAccessPdf"]:
                            reference["openAccessPdf"] = {"url":None}
                        related_papers.append(reference)
                        related_papers_title.append(reference["title"])
                    elif reference["title"] in related_papers_title or reference["title"] in self.ban_paper or reference["title"] in paper_list:
                        continue
                    elif reference["isOpenAccess"] == False or reference["openAccessPdf"] == None:
                        continue
                    else:
                        related_papers.append(reference)
                        related_papers_title.append(reference["title"])
            if result:
                break
        
        if len(related_papers) >= 200:
            related_papers = random.sample(related_papers,200)

        if rerank_query and llm:
            rerank_query_embbeding = llm.get_embbeding(rerank_query)
            rerank_query_embbeding = np.array(rerank_query_embbeding)
            related_papers = self.rerank_papers(rerank_query_embbeding, related_papers,llm)
            related_papers = [[paper["title"],paper["abstract"],paper["openAccessPdf"]["url"],paper["citationCount"],paper['year']] for paper in related_papers]
        else:
            related_papers = [[paper["title"],paper["abstract"],paper["openAccessPdf"]["url"],paper["citationCount"],paper['year']] for paper in related_papers]
            related_papers = sorted(related_papers,key = lambda x: x[3],reverse = True)
        print(f"Found {len(related_papers)} related papers")
        for paper in related_papers:
            url = paper[2]
            article = await self.read_arxiv_from_link_async(url, f"{paper[0]}.pdf")
            if not article:
                continue
            result = Result(paper[0],paper[1],article,paper[3],paper[4])
            return result
        print(f"Failed to find related papers of paper <{title}>; Citation:{need_citation}; Reference:{need_reference}")
        return None

    

    async def read_arxiv_from_link_async(self, pdf_link , filename):
        file_path = os.path.join(self.save_file, filename)
        if os.path.exists(file_path):
            article_dict = self.read_arxiv_from_path(file_path)
            return article_dict

        result = await self.download_pdf_async(pdf_link, file_path)
        if not result:
            print(f"Failed to download the PDF file: {filename}")
            return None
        try:
            article_dict = self.read_arxiv_from_path(file_path)
            return article_dict
        except Exception as e:
            print(f"Failed to read the article from the PDF file: {e}, {filename}")
            return None

    def read_arxiv_from_path(self, pdf_path):
        if not os.path.exists(pdf_path):
            print(f"The PDF file <{pdf_path}> does not exist.")
            return None
        try:
            article_dict = scipdf.parse_pdf_to_dict(pdf_path)
        except Exception as e:
            return None
        return article_dict


    async def download_pdf_async(self, pdf_link, save_path):
        if os.path.exists(save_path):
            print(f"The PDF file <{save_path}> already exists.")
            return True
        content = await fetch(pdf_link)
        if not content:
            print(f"Failed to download the PDF: {save_path}")
            return False
        try:
            with open(save_path, 'wb') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Failed to download the PDF file: {e}, {save_path}")
            return False


    def read_paper_title_abstract(self,article):
        title = article["title"]
        abstract = article["abstract"]
        paper_content = f"""
Title: {title}
Abstract: {abstract}
        """
        return paper_content
    

    def read_paper_title_abstract_introduction(self,article):
        title = article["title"]
        abstract = article["abstract"]
        introduction = article["sections"][0]["text"]
        paper_content = f"""
Title: {title}
Abstract: {abstract}
Introduction: {introduction}
        """
        return paper_content

    def read_paper_content(self,article):
        paper_content = self.read_paper_title_abstract(article)
        for section in article["sections"]:
            # paper_content += f"section: {section['heading']}\n content: {section['text']}\n ref_ids: {section['publication_ref']}\n"
            paper_content += f"Section: {section['heading']}\n{section['text']}\nthis section cite: {section['publication_ref']}\n"
        return paper_content
    
    def read_paper_content_with_ref(self,article):
        paper_content = self.read_paper_content(article)
        paper_content += "Section: References\n"
        for refer in article["references"]:
            ref_id = refer["ref_id"]
            title = refer["title"]
            year = refer["year"]
            paper_content += f"Ref_id:{ref_id} Title: {title} Year: ({year})\n"
        # paper_content += "</References>\n"
        return paper_content
