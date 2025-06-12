import openai
from ..config import settings
from ..models import File

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY, # DeepSeek API 兼容 OpenAI API Key
            base_url=settings.DEEPSEEK_API_BASE_URL
        )

    async def analyze_text(self, content: str) -> Dict[str, Any]:
        """分析文本内容，生成摘要和关键词"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的文本分析助手，请分析以下文本并生成摘要和关键词。"},
                    {"role": "user", "content": content}
                ]
            )
            return {
                "summary": response.choices[0].message.content,
                "keywords": self._extract_keywords(response.choices[0].message.content)
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {"summary": "", "keywords": []}

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """分析代码，生成代码说明和优化建议"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": f"你是一个专业的代码分析助手，请分析以下{language}代码并生成说明和优化建议。"},
                    {"role": "user", "content": code}
                ]
            )
            return {
                "description": response.choices[0].message.content,
                "suggestions": self._extract_suggestions(response.choices[0].message.content)
            }
        except Exception as e:
            print(f"Error analyzing code: {e}")
            return {"description": "", "suggestions": []}

    async def generate_file_tags(self, file: File, content: Optional[str] = None) -> List[str]:
        """为文件生成标签"""
        try:
            prompt = f"文件名: {file.name}\n"
            if content:
                prompt += f"内容预览: {content[:500]}...\n"
            prompt += "请为这个文件生成3-5个相关的标签。"

            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的文件分类助手，请根据文件名和内容生成合适的标签。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return self._extract_tags(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating tags: {e}")
            return []

    async def semantic_search(self, query: str, files: List[File]) -> List[File]:
        """基于语义的文件搜索"""
        try:
            # 获取查询的嵌入向量
            query_embedding = await self._get_embedding(query)
            
            # 计算相似度并排序
            scored_files = []
            for file in files:
                file_embedding = await self._get_embedding(file.name)
                similarity = self._cosine_similarity(query_embedding, file_embedding)
                scored_files.append((file, similarity))
            
            # 按相似度排序
            scored_files.sort(key=lambda x: x[1], reverse=True)
            return [file for file, _ in scored_files]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return files

    async def _get_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量"""
        try:
            response = await self.client.embeddings.create(
                model=settings.DEEPSEEK_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取实现
        words = text.lower().split()
        return list(set([w for w in words if len(w) > 3]))

    def _extract_suggestions(self, text: str) -> List[str]:
        """从文本中提取建议"""
        # 简单的建议提取实现
        suggestions = []
        for line in text.split('\n'):
            if line.strip().startswith('-') or line.strip().startswith('•'):
                suggestions.append(line.strip()[1:].strip())
        return suggestions

    def _extract_tags(self, text: str) -> List[str]:
        """从文本中提取标签"""
        # 简单的标签提取实现
        tags = []
        for line in text.split('\n'):
            if line.strip().startswith('#') or line.strip().startswith('标签:'):
                tags.extend([t.strip() for t in line.split(',')])
        return [t.strip('#').strip() for t in tags if t.strip()]

ai_service = AIService() 