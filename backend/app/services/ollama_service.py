"""
Ollama服务
封装与Ollama的交互，包括嵌入向量化和LLM调用
"""
import ollama
from typing import List, Dict, Any, Optional
import json
import re
from app.core.config import settings


class OllamaService:
    """Ollama服务类"""
    
    def __init__(self):
        """初始化Ollama客户端"""
        self.base_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.llm_model = settings.OLLAMA_LLM_MODEL
        # 配置Ollama客户端（如果需要自定义base_url）
        # ollama.Client(host=self.base_url)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的嵌入向量
        用于文档向量化和相似度计算
        
        注意：如果使用deepseek-r1:7b作为嵌入模型，可能需要特殊处理
        建议使用专门的嵌入模型如nomic-embed-text
        """
        try:
            # 截断过长的文本（嵌入模型通常有长度限制）
            max_length = 8192  # 大多数嵌入模型的最大长度
            if len(text) > max_length:
                text = text[:max_length]
            
            # 调用Ollama嵌入API
            response = ollama.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            
            if response and 'embedding' in response:
                return response['embedding']
            else:
                raise Exception("无法获取嵌入向量")
        except Exception as e:
            # 如果嵌入模型不可用，返回空向量或使用备用方案
            print(f"嵌入向量获取失败: {str(e)}")
            # 可以返回一个固定维度的零向量作为备用
            return [0.0] * 768  # 默认768维向量
    
    def compare_documents(self, document_text: str, regulation_text: str) -> Dict[str, Any]:
        """
        对比两个文档
        使用deepseek-r1:7b进行语义理解和对比分析
        返回不符合项的列表
        
        返回格式：
        {
            "issues": [
                {
                    "content": "不符合的内容",
                    "position": "位置信息",
                    "issue_type": "content_mismatch|missing|extra|format",
                    "severity": "critical|general|minor",
                    "regulation_clause": "对应的制度条款",
                    "reason": "不符合原因",
                    "suggestion": "修改建议"
                }
            ]
        }
        """
        # 构建提示词
        prompt = f"""你是一个专业的合规审查专家。请对比以下员工文档和制度文件，找出不符合制度要求的内容。

制度文件内容：
{regulation_text[:3000]}  # 限制长度避免超出token限制

员工文档内容：
{document_text[:3000]}  # 限制长度避免超出token限制

请仔细分析，找出以下类型的问题：
1. 内容不符：员工文档中的表述与制度要求不一致
2. 缺失项：制度要求但员工文档中缺失的内容
3. 多余项：员工文档中存在但制度未要求的内容
4. 格式不符：格式要求不符合制度规定

对于每个问题，请按以下JSON格式输出：
{{
    "issues": [
        {{
            "content": "不符合的具体内容（从员工文档中提取）",
            "position": "大致位置描述（如：第X段）",
            "issue_type": "问题类型（content_mismatch/missing/extra/format）",
            "severity": "严重程度（critical=严重必须修改，general=一般建议修改，minor=轻微可选修改）",
            "regulation_clause": "对应的制度条款内容",
            "reason": "不符合原因的详细说明",
            "suggestion": "具体的修改建议"
        }}
    ]
}}

只返回JSON格式，不要有其他说明文字。如果没有任何问题，返回 {{"issues": []}}。"""

        try:
            # 调用Ollama LLM
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的合规审查专家，擅长分析文档是否符合制度要求。请严格按照JSON格式输出结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.3,  # 降低温度以获得更稳定的结果
                }
            )
            
            # 提取响应内容
            if response and 'message' in response:
                content = response['message'].get('content', '')
                
                # 尝试从响应中提取JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                else:
                    # 如果无法解析JSON，返回空结果
                    print(f"无法解析LLM响应为JSON: {content[:200]}")
                    return {"issues": []}
            else:
                return {"issues": []}
                
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            return {"issues": []}
        except Exception as e:
            print(f"文档对比失败: {str(e)}")
            return {"issues": []}
    
    def generate_enhanced_suggestion(
        self, 
        issue_description: str, 
        regulation_clause: str,
        issue_type: str = "",
        severity: str = ""
    ) -> Dict[str, str]:
        """
        生成增强的改进建议
        提供更详细、更实用的改进建议，包括：
        - 详细的问题分析
        - 具体的修改建议
        - 改进后的内容示例
        
        返回格式：
        {
            "reason": "不符合原因的详细说明",
            "suggestion": "具体的修改建议",
            "detailed_analysis": "详细的问题分析",
            "improved_content": "改进后的内容示例"
        }
        """
        severity_text = {
            "critical": "严重",
            "general": "一般",
            "minor": "轻微"
        }.get(severity, "一般")
        
        issue_type_text = {
            "content_mismatch": "内容不符",
            "missing": "缺失项",
            "extra": "多余项",
            "format": "格式不符"
        }.get(issue_type, "问题")
        
        prompt = f"""你是一个专业的合规审查专家。请为以下合规问题生成详细的分析和改进建议。

问题信息：
- 问题类型：{issue_type_text}
- 严重程度：{severity_text}
- 问题描述：{issue_description}
- 对应的制度条款：{regulation_clause}

请生成以下内容：

1. **详细问题分析**：深入分析为什么这个问题不符合制度要求，可能造成的影响和风险。

2. **具体修改建议**：提供清晰、可操作的修改建议，包括：
   - 应该修改什么内容
   - 如何修改
   - 修改后的预期效果

3. **改进后的内容示例**：如果可能，提供一个改进后的内容示例，展示修改后的正确表述。

请按以下JSON格式输出：
{{
    "reason": "不符合原因的详细说明（2-3句话）",
    "suggestion": "具体的修改建议（详细说明如何修改，3-5句话）",
    "detailed_analysis": "详细的问题分析（分析问题原因、影响和风险，5-8句话）",
    "improved_content": "改进后的内容示例（如果适用，提供修改后的正确表述）"
}}

只返回JSON格式，不要有其他说明文字。"""

        try:
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的合规审查专家，擅长深入分析合规问题并提供详细、实用的改进建议。请严格按照JSON格式输出结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.6,  # 稍微提高温度以获得更丰富的建议
                }
            )
            
            if response and 'message' in response:
                content = response['message'].get('content', '')
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                else:
                    return {
                        "reason": "无法生成详细说明",
                        "suggestion": "请参考制度条款进行修改",
                        "detailed_analysis": "",
                        "improved_content": ""
                    }
            else:
                return {
                    "reason": "无法生成详细说明",
                    "suggestion": "请参考制度条款进行修改",
                    "detailed_analysis": "",
                    "improved_content": ""
                }
                
        except Exception as e:
            print(f"生成增强建议失败: {str(e)}")
            return {
                "reason": "生成说明时出错",
                "suggestion": "请参考制度条款进行修改",
                "detailed_analysis": "",
                "improved_content": ""
            }
    
    def generate_annotation(self, issue_description: str, regulation_clause: str) -> Dict[str, str]:
        """
        生成标注信息
        根据识别出的问题，生成详细的原因说明和修改建议
        
        返回格式：
        {
            "reason": "不符合原因的详细说明",
            "suggestion": "具体的修改建议"
        }
        """
        prompt = f"""请为以下合规问题生成详细的说明和建议：

问题描述：{issue_description}

对应的制度条款：{regulation_clause}

请生成：
1. 不符合原因的详细说明（解释为什么不符合制度要求）
2. 具体的修改建议（说明应该如何修改以符合制度要求）

请按以下JSON格式输出：
{{
    "reason": "不符合原因的详细说明",
    "suggestion": "具体的修改建议"
}}"""

        try:
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的合规审查专家，擅长生成详细的合规问题说明和修改建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.5,
                }
            )
            
            if response and 'message' in response:
                content = response['message'].get('content', '')
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                else:
                    return {
                        "reason": "无法生成详细说明",
                        "suggestion": "请参考制度条款进行修改"
                    }
            else:
                return {
                    "reason": "无法生成详细说明",
                    "suggestion": "请参考制度条款进行修改"
                }
                
        except Exception as e:
            print(f"生成标注信息失败: {str(e)}")
            return {
                "reason": "生成说明时出错",
                "suggestion": "请参考制度条款进行修改"
            }

