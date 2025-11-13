"""
社区路由 - 互助社区帖子和评论
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import CommunityPost, Comment, User, ContentLike, PostReport
from schemas import PostCreate, PostResponse, CommentCreate, CommentResponse
from auth import get_current_active_user, get_optional_user

router = APIRouter()


@router.post("/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """发布社区帖子（默认匿名，直接发布）"""
    new_post = CommunityPost(
        author_id=current_user.id,
        category=post_data.category,
        content=post_data.content,
        tags=post_data.tags,
        is_approved=True  # 直接发布，不需要审核
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    # 获取作者信息
    author = db.query(User).filter(User.id == new_post.author_id).first()
    author_name = author.nickname if author and author.nickname else f"用户{new_post.author_id % 10000}"
    author_nickname = author.nickname if author else None
    author_role = author.role.value if author else None
    
    post_dict = {
        "id": new_post.id,
        "author_id": new_post.author_id,
        "author_name": author_name,
        "author_nickname": author_nickname,
        "author_role": author_role,
        "category": new_post.category,
        "content": new_post.content,
        "tags": new_post.tags,
        "like_count": new_post.like_count,
        "comment_count": new_post.comment_count,
        "is_liked": False,
        "created_at": new_post.created_at,
    }
    
    return PostResponse(**post_dict)


@router.get("/posts", response_model=List[PostResponse])
def get_posts(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取社区帖子列表（所有用户可见，排除被多人举报的帖子）"""
    query = db.query(CommunityPost).filter(
        CommunityPost.is_approved == True,
        CommunityPost.is_deleted == False,
        CommunityPost.report_count < 3  # 举报次数少于3次的帖子才显示
    )
    
    if category:
        query = query.filter(CommunityPost.category == category)
    
    posts = query.order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构建响应，包含作者信息和点赞状态
    result = []
    for post in posts:
        # 获取作者信息
        author = db.query(User).filter(User.id == post.author_id).first()
        author_name = author.nickname if author and author.nickname else f"用户{post.author_id % 10000}"
        author_nickname = author.nickname if author else None
        author_role = author.role.value if author else None
        
        # 检查当前用户是否已点赞
        is_liked = False
        if current_user:
            like = db.query(ContentLike).filter(
                ContentLike.user_id == current_user.id,
                ContentLike.content_type == "post",
                ContentLike.content_id == post.id
            ).first()
            is_liked = like is not None
        
        post_dict = {
            "id": post.id,
            "author_id": post.author_id,
            "author_name": author_name,
            "author_nickname": author_nickname,
            "author_role": author_role,
            "category": post.category,
            "content": post.content,
            "tags": post.tags,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "is_liked": is_liked,
            "created_at": post.created_at,
        }
        result.append(PostResponse(**post_dict))
    
    return result


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post_detail(
    post_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取帖子详情"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post or post.is_deleted:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 获取作者信息
    author = db.query(User).filter(User.id == post.author_id).first()
    author_name = author.nickname if author and author.nickname else f"用户{post.author_id % 10000}"
    author_nickname = author.nickname if author else None
    author_role = author.role.value if author else None
    
    # 检查当前用户是否已点赞
    is_liked = False
    if current_user:
        like = db.query(ContentLike).filter(
            ContentLike.user_id == current_user.id,
            ContentLike.content_type == "post",
            ContentLike.content_id == post.id
        ).first()
        is_liked = like is not None
    
    post_dict = {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": author_name,
        "author_nickname": author_nickname,
        "author_role": author_role,
        "category": post.category,
        "content": post.content,
        "tags": post.tags,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "is_liked": is_liked,
        "created_at": post.created_at,
    }
    
    return PostResponse(**post_dict)


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞帖子（防止重复点赞）"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 检查是否已点赞
    existing_like = db.query(ContentLike).filter(
        ContentLike.user_id == current_user.id,
        ContentLike.content_type == "post",
        ContentLike.content_id == post_id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        post.like_count = max(0, post.like_count - 1)
        db.commit()
        return {"message": "已取消点赞", "like_count": post.like_count, "is_liked": False}
    else:
        # 点赞
        new_like = ContentLike(
            user_id=current_user.id,
            content_type="post",
            content_id=post_id
        )
        db.add(new_like)
        post.like_count += 1
        db.commit()
        return {"message": "点赞成功", "like_count": post.like_count, "is_liked": True}


@router.post("/comments", response_model=CommentResponse)
def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """发布评论"""
    # 检查帖子是否存在
    post = db.query(CommunityPost).filter(CommunityPost.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    new_comment = Comment(
        post_id=comment_data.post_id,
        user_id=current_user.id,
        content=comment_data.content,
        is_approved=True  # 直接发布，不需要审核
    )
    
    db.add(new_comment)
    
    # 更新帖子评论数
    post.comment_count += 1
    
    db.commit()
    db.refresh(new_comment)
    
    # 获取用户信息
    user = db.query(User).filter(User.id == new_comment.user_id).first()
    user_name = user.nickname if user and user.nickname else f"用户{new_comment.user_id % 10000}"
    user_nickname = user.nickname if user else None
    
    comment_dict = {
        "id": new_comment.id,
        "post_id": new_comment.post_id,
        "user_id": new_comment.user_id,
        "user_name": user_name,
        "user_nickname": user_nickname,
        "content": new_comment.content,
        "like_count": new_comment.like_count,
        "is_liked": False,
        "created_at": new_comment.created_at,
    }
    
    return CommentResponse(**comment_dict)


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(
    post_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取帖子的评论列表"""
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.is_approved == True
    ).order_by(Comment.created_at.asc()).all()
    
    # 构建响应，包含用户信息和点赞状态
    result = []
    for comment in comments:
        # 获取用户信息
        user = db.query(User).filter(User.id == comment.user_id).first()
        user_name = user.nickname if user and user.nickname else f"用户{comment.user_id % 10000}"
        user_nickname = user.nickname if user else None
        
        # 检查当前用户是否已点赞
        is_liked = False
        if current_user:
            like = db.query(ContentLike).filter(
                ContentLike.user_id == current_user.id,
                ContentLike.content_type == "comment",
                ContentLike.content_id == comment.id
            ).first()
            is_liked = like is not None
        
        comment_dict = {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "user_name": user_name,
            "user_nickname": user_nickname,
            "content": comment.content,
            "like_count": comment.like_count,
            "is_liked": is_liked,
            "created_at": comment.created_at,
        }
        result.append(CommentResponse(**comment_dict))
    
    return result


@router.post("/posts/{post_id}/report")
def report_post(
    post_id: int,
    reason: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """举报帖子"""
    # 检查帖子是否存在
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 检查是否已经举报过
    existing_report = db.query(PostReport).filter(
        PostReport.post_id == post_id,
        PostReport.user_id == current_user.id
    ).first()
    
    if existing_report:
        raise HTTPException(status_code=400, detail="您已经举报过该帖子")
    
    # 创建举报记录
    new_report = PostReport(
        post_id=post_id,
        user_id=current_user.id,
        reason=reason
    )
    db.add(new_report)
    
    # 更新帖子举报次数
    post.report_count += 1
    
    # 如果举报次数达到3次，自动设置为未审核状态
    if post.report_count >= 3:
        post.is_approved = False
    
    db.commit()
    
    return {
        "message": "举报成功",
        "report_count": post.report_count,
        "is_approved": post.is_approved
    }
