import json
from models.ai import FileAnalysis
from database import db_session
import os
from dotenv import load_dotenv
import requests
import numpy as np
import mimetypes
import chardet
from services.storage import LocalStorage, S3Storage

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
    
    def test_connection(self, api_key):
        """测试API连接"""
        try:
            print(f"正在测试API连接，使用密钥: {api_key[:8]}...")
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '测试连接'},
                        {'role': 'user', 'content': 'Hello'}
                    ],
                    'max_tokens': 5
                }
            )
            
            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
            return True
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {str(e)}")
            return False
        except Exception as e:
            print(f"其他错误: {str(e)}")
            return False

    def get_storage_client(self, storage):
        """获取存储客户端"""
        config = json.loads(storage.config)
        if storage.type == 'local':
            return LocalStorage(config['path'])
        elif storage.type == 's3':
            return S3Storage(
                access_key=config['access_key'],
                secret_key=config['secret_key'],
                bucket=config['bucket'],
                region=config['region']
            )
        raise ValueError(f'不支持的存储类型: {storage.type}')

    def can_analyze_file(self, file_type):
        """检查文件是否可以分析"""
        # 只分析文本类型的文件
        text_types = [
            'text/',
            'application/json',
            'application/xml',
            'application/javascript',
            'application/x-python',
            'application/x-java',
            'application/x-c',
            'application/x-cpp',
            'application/x-csharp',
            'application/x-php',
            'application/x-ruby',
            'application/x-shellscript',
            'application/x-yaml',
            'application/x-markdown',
            'application/x-latex',
            'application/x-tex',
            'application/x-html',
            'application/x-css'
        ]
        return any(file_type.startswith(t) for t in text_types)

    def decode_file_content(self, content):
        """解码文件内容"""
        # 检测编码
        result = chardet.detect(content)
        encoding = result['encoding'] or 'utf-8'
        
        try:
            # 尝试解码
            return content.decode(encoding)
        except UnicodeDecodeError:
            # 如果失败，尝试其他常见编码
            for enc in ['utf-8', 'gbk', 'gb2312', 'ascii']:
                try:
                    return content.decode(enc)
                except UnicodeDecodeError:
                    continue
            raise ValueError('无法解码文件内容')

    def analyze_file_content(self, file_content, file_id, file_type):
        """分析文件内容并生成摘要、标签和情感分析"""
        try:
            # 检查文件类型
            if not self.can_analyze_file(file_type):
                raise ValueError('不支持分析此类型的文件')

            # 解码文件内容
            text_content = self.decode_file_content(file_content)
            
            # 使用DeepSeek API生成内容摘要
            summary_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("apiKey")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '你是一个专业的文件分析助手。请为以下内容生成简洁的摘要。'},
                        {'role': 'user', 'content': text_content[:4000]}  # 限制内容长度
                    ],
                    'temperature': self.config.get('temperature', 0.7),
                    'max_tokens': 500
                }
            )
            
            if summary_response.status_code != 200:
                raise ValueError(f'生成摘要失败: {summary_response.text}')
                
            summary = summary_response.json()['choices'][0]['message']['content']

            # 生成标签
            tags_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("apiKey")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '请为以下内容生成5-10个关键词标签，以逗号分隔。'},
                        {'role': 'user', 'content': text_content[:2000]}
                    ],
                    'temperature': self.config.get('temperature', 0.7),
                    'max_tokens': 100
                }
            )
            
            if tags_response.status_code != 200:
                raise ValueError(f'生成标签失败: {tags_response.text}')
                
            tags = [tag.strip() for tag in tags_response.json()['choices'][0]['message']['content'].split(',')]

            # 情感分析
            sentiment_response = requests.post(
                f'{self.api_base}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.config.get("apiKey")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '请分析以下内容的情感倾向，返回一个-1到1之间的数字，-1表示非常负面，0表示中性，1表示非常正面。'},
                        {'role': 'user', 'content': text_content[:2000]}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 10
                }
            )
            
            if sentiment_response.status_code != 200:
                raise ValueError(f'情感分析失败: {sentiment_response.text}')
                
            sentiment_score = float(sentiment_response.json()['choices'][0]['message']['content'].strip())

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
            db_session.rollback()
            raise

    def get_file_analysis(self, file_id):
        """获取文件的分析结果"""
        return db_session.query(FileAnalysis).filter_by(file_id=file_id).first()

    def search_similar_files(self, query, semantic=True, content=False, limit=5):
        """搜索相似文件"""
        try:
            if semantic:
                # 使用DeepSeek API进行语义搜索
                response = requests.post(
                    f'{self.api_base}/embeddings',
                    headers={
                        'Authorization': f'Bearer {self.config.get("apiKey")}',
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

            else:
                # 使用传统关键词搜索
                files = db_session.query(File).filter(
                    File.name.ilike(f'%{query}%')
                ).limit(limit).all()
                
                if content:
                    # 如果启用内容搜索，也搜索文件内容
                    content_files = db_session.query(File).filter(
                        File.content.ilike(f'%{query}%')
                    ).limit(limit).all()
                    files.extend(content_files)
                
                return files

        except Exception as e:
            print(f"搜索过程中出错: {str(e)}")
            return [] 