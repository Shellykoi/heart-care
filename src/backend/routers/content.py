"""
健康科普内容路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Content
from schemas import ContentCreate, ContentResponse
from auth import get_current_active_user

router = APIRouter()


@router.get("/list", response_model=List[ContentResponse])
def get_content_list(
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取科普内容列表
    - 支持按类型、分类筛选
    - 分页查询
    """
    query = db.query(Content).filter(Content.is_published == True)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if category:
        query = query.filter(Content.category == category)
    
    contents = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    
    return contents


@router.get("/{content_id}", response_model=ContentResponse)
def get_content_detail(content_id: int, db: Session = Depends(get_db)):
    """获取内容详情"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    # 增加浏览量
    content.view_count += 1
    db.commit()
    
    return content


@router.post("/{content_id}/like")
def like_content(
    content_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """点赞内容"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    content.like_count += 1
    db.commit()
    
    return {"message": "点赞成功", "like_count": content.like_count}
