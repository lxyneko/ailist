import os
from typing import Optional, Dict, Any
import mimetypes
from pathlib import Path
import magic
import markdown
from PIL import Image
import fitz  # PyMuPDF

class FilePreview:
    SUPPORTED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    SUPPORTED_DOCUMENT_TYPES = {'.pdf', '.doc', '.docx', '.txt', '.md'}
    SUPPORTED_CODE_TYPES = {'.py', '.js', '.ts', '.html', '.css', '.scss', '.json', '.xml'}

    @staticmethod
    def get_preview_type(file_path: str) -> str:
        """获取文件预览类型"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in FilePreview.SUPPORTED_IMAGE_TYPES:
            return "image"
        elif ext in FilePreview.SUPPORTED_DOCUMENT_TYPES:
            return "document"
        elif ext in FilePreview.SUPPORTED_CODE_TYPES:
            return "code"
        else:
            return "unknown"

    @staticmethod
    async def get_preview_data(file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件预览数据"""
        preview_type = FilePreview.get_preview_type(file_path)
        
        if preview_type == "image":
            return await FilePreview._get_image_preview(file_path)
        elif preview_type == "document":
            return await FilePreview._get_document_preview(file_path)
        elif preview_type == "code":
            return await FilePreview._get_code_preview(file_path)
        return None

    @staticmethod
    async def _get_image_preview(file_path: str) -> Dict[str, Any]:
        """获取图片预览数据"""
        with Image.open(file_path) as img:
            return {
                "type": "image",
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }

    @staticmethod
    async def _get_document_preview(file_path: str) -> Dict[str, Any]:
        """获取文档预览数据"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return await FilePreview._get_pdf_preview(file_path)
        elif ext == '.md':
            return await FilePreview._get_markdown_preview(file_path)
        elif ext == '.txt':
            return await FilePreview._get_text_preview(file_path)
        return None

    @staticmethod
    async def _get_pdf_preview(file_path: str) -> Dict[str, Any]:
        """获取PDF预览数据"""
        doc = fitz.open(file_path)
        return {
            "type": "pdf",
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", "")
        }

    @staticmethod
    async def _get_markdown_preview(file_path: str) -> Dict[str, Any]:
        """获取Markdown预览数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            html = markdown.markdown(content)
            return {
                "type": "markdown",
                "html": html
            }

    @staticmethod
    async def _get_text_preview(file_path: str) -> Dict[str, Any]:
        """获取文本预览数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return {
                "type": "text",
                "content": content
            }

    @staticmethod
    async def _get_code_preview(file_path: str) -> Dict[str, Any]:
        """获取代码预览数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return {
                "type": "code",
                "content": content,
                "language": os.path.splitext(file_path)[1][1:]
            } 