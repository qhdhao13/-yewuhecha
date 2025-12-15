"""
审查服务
处理文档审查的核心业务逻辑
"""
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.document import Document
from app.models.regulation import Regulation
from app.models.annotation import Annotation
from app.services.ollama_service import OllamaService
from app.services.document_parser import DocumentParser
from datetime import datetime
import os


class ReviewService:
    """审查服务类"""
    
    @staticmethod
    def process_review(review_id: int):
        """
        处理审查任务
        这是核心的审查逻辑，包括：
        1. 提取文档内容
        2. 使用Ollama进行语义对比
        3. 识别不符合项
        4. 创建标注记录
        
        注意：此方法在后台任务中运行，需要创建新的数据库会话
        """
        # 创建新的数据库会话（后台任务需要）
        from app.core.database import SessionLocal
        db = SessionLocal()
        
        try:
            # 1. 获取审查记录、文档和制度
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                print(f"审查记录 {review_id} 不存在")
                return
            
            document = db.query(Document).filter(Document.id == review.document_id).first()
            regulation = db.query(Regulation).filter(Regulation.id == review.regulation_id).first()
            
            if not document or not regulation:
                review.status = "failed"
                db.commit()
                print("文档或制度不存在")
                return
            
            # 2. 解析文档内容（如果还没有解析过）
            document_text = document.content
            if not document_text and document.file_path:
                try:
                    # 构建文件完整路径（file_path存储的是相对路径）
                    from app.core.config import settings
                    if os.path.isabs(document.file_path):
                        doc_full_path = document.file_path
                    else:
                        doc_full_path = os.path.join(settings.UPLOAD_DIR, document.file_path)
                    
                    # 检查文件是否存在
                    if os.path.exists(doc_full_path):
                        document_text = DocumentParser.parse_file(doc_full_path)
                        # 保存解析后的内容
                        document.content = document_text
                        db.commit()
                    else:
                        raise Exception(f"文档文件不存在: {doc_full_path}")
                except Exception as e:
                    print(f"解析文档失败: {str(e)}")
                    review.status = "failed"
                    db.commit()
                    return
            
            # 解析制度文件内容（如果还没有解析过）
            regulation_text = regulation.content
            if not regulation_text and regulation.file_path:
                try:
                    # 构建文件完整路径（file_path存储的是相对路径）
                    from app.core.config import settings
                    if os.path.isabs(regulation.file_path):
                        reg_full_path = regulation.file_path
                    else:
                        reg_full_path = os.path.join(settings.UPLOAD_DIR, regulation.file_path)
                    
                    if os.path.exists(reg_full_path):
                        regulation_text = DocumentParser.parse_file(reg_full_path)
                        # 保存解析后的内容
                        regulation.content = regulation_text
                        db.commit()
                    else:
                        raise Exception(f"制度文件不存在: {reg_full_path}")
                except Exception as e:
                    print(f"解析制度文件失败: {str(e)}")
                    review.status = "failed"
                    db.commit()
                    return
            
            if not document_text or not regulation_text:
                review.status = "failed"
                db.commit()
                print("文档或制度内容为空")
                return
            
            # 3. 使用Ollama进行对比分析
            ollama_service = OllamaService()
            comparison_result = ollama_service.compare_documents(
                document_text=document_text,
                regulation_text=regulation_text
            )
            
            # 4. 生成标注记录
            issues = comparison_result.get("issues", [])
            
            # 统计信息
            critical_count = 0
            general_count = 0
            minor_count = 0
            
            # 创建标注记录
            for issue in issues:
                # 确定严重程度计数
                severity = issue.get("severity", "minor")
                if severity == "critical":
                    critical_count += 1
                elif severity == "general":
                    general_count += 1
                else:
                    minor_count += 1
                
                # 如果标注信息不完整，使用LLM生成
                reason = issue.get("reason", "")
                suggestion = issue.get("suggestion", "")
                
                if not reason or not suggestion:
                    annotation_info = ollama_service.generate_annotation(
                        issue_description=issue.get("content", ""),
                        regulation_clause=issue.get("regulation_clause", "")
                    )
                    if not reason:
                        reason = annotation_info.get("reason", "")
                    if not suggestion:
                        suggestion = annotation_info.get("suggestion", "")
                
                # 创建标注记录
                annotation = Annotation(
                    review_id=review_id,
                    document_id=review.document_id,
                    regulation_id=review.regulation_id,
                    position=issue.get("position", ""),
                    content=issue.get("content", ""),
                    regulation_clause=issue.get("regulation_clause", ""),
                    issue_type=issue.get("issue_type", "content_mismatch"),
                    severity=severity,
                    reason=reason,
                    suggestion=suggestion,
                    status="pending",
                    reviewer=review.reviewer
                )
                db.add(annotation)
            
            # 5. 更新审查状态和统计信息
            review.status = "completed"
            review.total_issues = len(issues)
            review.critical_count = critical_count
            review.general_count = general_count
            review.minor_count = minor_count
            review.completed_time = datetime.now()
            
            # 更新文档状态
            document.status = "completed"
            
            db.commit()
            print(f"审查任务 {review_id} 完成，共发现 {len(issues)} 个不符合项")
            
        except Exception as e:
            print(f"处理审查任务失败: {str(e)}")
            # 更新审查状态为失败
            try:
                review = db.query(Review).filter(Review.id == review_id).first()
                if review:
                    review.status = "failed"
                    db.commit()
            except:
                pass
        finally:
            # 关闭数据库会话
            db.close()

