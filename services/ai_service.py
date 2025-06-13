import json
from models.ai import FileAnalysis
from database import db_session
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class AIService:
    def __init__(self):
        self.config = self.load_config()
        self.api_base = 'https://api.deepseek.com/v1'
    
    def load_config(self):
        """加载AI配置"""
        config_file = 'ai_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def analyze_file_content(self, file_content, file_id):
        """分析文件内容并生成摘要、标签和情感分析"""
        try:
            # 使用DeepSeek API生成内容摘要
            summary_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("deepseek_api_key")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-coder-33b-instruct',
                    'messages': [
                        {'role': 'system', 'content': '你是一个专业的文件分析助手。请为以下内容生成简洁的摘要。'},
                        {'role': 'user', 'content': file_content[:4000]}  # 限制内容长度
                    ],
                    'temperature': 0.7,
                    'max_tokens': 500
                }
            )
            summary = summary_response.json()['choices'][0]['message']['content']

            # 生成标签建议
            tags_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("deepseek_api_key")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-coder-33b-instruct',
                    'messages': [
                        {'role': 'system', 'content': '请为以下内容生成3-5个最相关的标签，以JSON数组格式返回。'},
                        {'role': 'user', 'content': file_content[:4000]}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 200
                }
            )
            tags = json.loads(tags_response.json()['choices'][0]['message']['content'])

            # 情感分析
            sentiment_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("deepseek_api_key")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-coder-33b-instruct',
                    'messages': [
                        {'role': 'system', 'content': '请分析以下内容的情感倾向，返回-100到100之间的分数，-100表示极度负面，100表示极度正面。'},
                        {'role': 'user', 'content': file_content[:4000]}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 50
                }
            )
            sentiment_score = int(sentiment_response.json()['choices'][0]['message']['content'])

            # 保存分析结果
            analysis = FileAnalysis(
                file_id=file_id,
                content_summary=summary,
                suggested_tags=json.dumps(tags),
                sentiment_score=sentiment_score
            )
            db_session.add(analysis)
            db_session.commit()

            return analysis

        except Exception as e:
            print(f"AI分析过程中出错: {str(e)}")
            return None

    def get_file_analysis(self, file_id):
        """获取文件的分析结果"""
        return db_session.query(FileAnalysis).filter_by(file_id=file_id).first()

    def search_similar_files(self, query, limit=5):
        """搜索相似文件"""
        try:
            # 使用DeepSeek API进行语义搜索
            response = requests.post(
                f'{self.api_base}/embeddings',
                headers={
                    'Authorization': f'Bearer {self.config.get("deepseek_api_key")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-embed',
                    'input': query,
                    'encoding_format': 'float'
                }
            )
            query_embedding = response.json()['data'][0]['embedding']

            # TODO: 实现向量数据库存储和检索
            # 这里需要添加向量数据库支持，如Pinecone或Milvus
            return []

        except Exception as e:
            print(f"搜索过程中出错: {str(e)}")
            return [] 