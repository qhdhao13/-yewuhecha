"""
文档解析服务
解析PDF、Word等格式的文档，提取文本内容
"""
import os
from typing import Optional
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document as DocxDocument


class DocumentParser:
    """文档解析器"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        解析PDF文件，提取文本内容
        优先使用pdfplumber（更准确），失败则使用PyPDF2
        """
        text = ""
        try:
            # 尝试使用pdfplumber（支持更多格式）
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            # 如果pdfplumber失败，尝试PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                raise Exception(f"PDF解析失败: {str(e2)}")
        
        return text.strip()
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        解析Word文档（.docx），提取文本内容
        注意：.doc格式（旧版Word）需要额外工具，这里只支持.docx
        """
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Word文档解析失败: {str(e)}")
    
    @staticmethod
    def parse_doc(file_path: str) -> str:
        """
        解析旧版Word文档（.doc）
        注意：需要安装python-docx2txt或其他工具
        目前返回提示信息
        """
        raise Exception("暂不支持.doc格式，请转换为.docx格式")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """
        解析纯文本文件
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as file:
                return file.read()
    
    @staticmethod
    def parse_file(file_path: str) -> str:
        """
        根据文件类型自动选择解析方法
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif file_ext == '.docx':
            return DocumentParser.parse_docx(file_path)
        elif file_ext == '.doc':
            return DocumentParser.parse_doc(file_path)
        elif file_ext in ['.txt', '.md']:
            return DocumentParser.parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

