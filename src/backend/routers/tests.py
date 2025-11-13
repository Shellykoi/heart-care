"""
心理测评路由 - 测评量表和报告管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import TestScale, TestReport, User
from schemas import TestScaleResponse, TestReportCreate, TestReportResponse
from auth import get_current_active_user

router = APIRouter()


@router.get("/scales", response_model=List[TestScaleResponse])
def get_test_scales(db: Session = Depends(get_db)):
    """获取所有测评量表列表"""
    scales = db.query(TestScale).filter(TestScale.is_active == True).all()
    return scales


@router.get("/scales/{scale_id}", response_model=TestScaleResponse)
def get_test_scale_detail(scale_id: int, db: Session = Depends(get_db)):
    """获取测评量表详情"""
    scale = db.query(TestScale).filter(TestScale.id == scale_id).first()
    
    if not scale:
        raise HTTPException(status_code=404, detail="测评量表不存在")
    
    return scale


@router.post("/submit", response_model=TestReportResponse)
def submit_test_report(
    report_data: TestReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """提交测评结果"""
    # 检查量表是否存在
    scale = db.query(TestScale).filter(TestScale.id == report_data.scale_id).first()
    if not scale:
        raise HTTPException(status_code=404, detail="测评量表不存在")
    
    # 创建测评报告
    new_report = TestReport(
        user_id=current_user.id,
        scale_id=report_data.scale_id,
        score=report_data.score,
        level=report_data.level,
        result_json=report_data.result_json
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.get("/reports/mine", response_model=List[TestReportResponse])
def get_my_test_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的测评报告列表"""
    reports = db.query(TestReport).filter(
        TestReport.user_id == current_user.id
    ).order_by(TestReport.created_at.desc()).all()
    
    return reports


@router.get("/reports/{report_id}", response_model=TestReportResponse)
def get_test_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取测评报告详情"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="测评报告不存在")
    
    # 检查权限
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此报告")
    
    return report
