"""
南湖心理咨询管理平台 - FastAPI 后端主入口
技术栈：FastAPI + MySQL 5.7 + SQLAlchemy
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import traceback

from database import get_db, engine
from models import Base
from routers import auth, users, counselors, appointments, tests, content, community, admin

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="南湖心理咨询管理平台 API",
    description="提供心理咨询预约、测评、科普、社区等功能的 RESTful API",
    version="1.0.0"
)

# 配置 CORS 跨域
# 开发环境：允许所有localhost和127.0.0.1的请求
# 生产环境：应该只允许特定域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",   
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
        "http://localhost:3010",
        "http://localhost:3011",
        "http://localhost:3012",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:3006",
        "http://127.0.0.1:3007",
        "http://127.0.0.1:3008",
        "http://127.0.0.1:3009",
        "http://127.0.0.1:3010",
        "http://127.0.0.1:3011",
        "http://127.0.0.1:3012",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
    max_age=3600,  # 预检请求缓存时间（秒）
)


# 添加OPTIONS请求处理（CORS预检请求）
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """处理所有OPTIONS预检请求"""
    # 获取请求的Origin头
    origin = request.headers.get("Origin")
    
    # 如果Origin在允许列表中，返回它；否则返回第一个允许的origin
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
        "http://localhost:3010",
        "http://localhost:3011",
        "http://localhost:3012",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:3006",
        "http://127.0.0.1:3007",
        "http://127.0.0.1:3008",
        "http://127.0.0.1:3009",
        "http://127.0.0.1:3010",
        "http://127.0.0.1:3011",
        "http://127.0.0.1:3012",
        "http://127.0.0.1:5173",
    ]
    
    # 如果Origin在允许列表中，使用它；否则使用第一个
    allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
    
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        },
        content={}
    )

# 添加 HTTPException 异常处理器（确保所有 HTTP 错误都包含 CORS 头）
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常，确保包含 CORS 头"""
    origin = request.headers.get("Origin")
    allowed_origins = [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
        "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
        "http://localhost:3006", "http://localhost:3007", "http://localhost:3008",
        "http://localhost:3009", "http://localhost:3010", "http://localhost:3011",
        "http://localhost:3012", "http://localhost:5173",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
        "http://127.0.0.1:3003", "http://127.0.0.1:3004", "http://127.0.0.1:3005",
        "http://127.0.0.1:3006", "http://127.0.0.1:3007", "http://127.0.0.1:3008",
        "http://127.0.0.1:3009", "http://127.0.0.1:3010", "http://127.0.0.1:3011",
        "http://127.0.0.1:3012", "http://127.0.0.1:5173",
    ]
    allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
    
    return JSONResponse(
        status_code=exc.status_code,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        content={
            "detail": exc.detail
        }
    )

# 添加 ValidationError 异常处理器（捕获 422 错误）
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误（422）"""
    import logging
    logger = logging.getLogger(__name__)
    errors = exc.errors()
    logger.error(f"请求验证失败: {errors}")
    logger.error(f"请求路径: {request.url.path}")
    logger.error(f"请求方法: {request.method}")
    
    # 检查是否是认证相关的错误（token 缺失或格式错误）
    # OAuth2PasswordBearer 在 token 缺失时会抛出验证错误
    auth_related = False
    for error in errors:
        error_loc = error.get("loc", [])
        error_msg = str(error.get("msg", "")).lower()
        error_type = str(error.get("type", "")).lower()
        
        # 将 error_loc 转换为字符串以便检查
        error_loc_str = str(error_loc).lower()
        
        # 检查是否是认证相关的错误
        # 1. 位置包含 "header" 和 "authorization"
        # 2. 位置包含 "query" 和 "token"（某些情况下 token 可能在 query 中）
        # 3. 错误消息包含 "authorization" 或 "token" 或 "credentials"
        # 4. 错误类型是 "value_error.missing" 且位置包含 "authorization" 或 "token"
        # 5. 错误类型是 "value_error.missing" 且是 header 字段
        if (
            (isinstance(error_loc, list) and "header" in error_loc and "authorization" in error_loc) or
            (isinstance(error_loc, list) and len(error_loc) >= 2 and error_loc[0] == "header" and "authorization" in error_loc_str) or
            "authorization" in error_loc_str or
            (error_type == "value_error.missing" and ("authorization" in error_loc_str or "token" in error_loc_str)) or
            "authorization" in error_msg or
            "token" in error_msg or
            "credentials" in error_msg or
            (error_type == "value_error.missing" and isinstance(error_loc, list) and len(error_loc) > 0 and error_loc[0] == "header")
        ):
            auth_related = True
            logger.warning(f"[validation_exception_handler] 检测到认证相关错误: {error}")
            break
    
    # 如果是认证错误，返回 401 而不是 422
    if auth_related:
        origin = request.headers.get("Origin")
        allowed_origins = [
            "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
            "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
            "http://localhost:3006", "http://localhost:3007", "http://localhost:3008",
            "http://localhost:3009", "http://localhost:3010", "http://localhost:3011",
            "http://localhost:3012", "http://localhost:5173",
            "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
            "http://127.0.0.1:3003", "http://127.0.0.1:3004", "http://127.0.0.1:3005",
            "http://127.0.0.1:3006", "http://127.0.0.1:3007", "http://127.0.0.1:3008",
            "http://127.0.0.1:3009", "http://127.0.0.1:3010", "http://127.0.0.1:3011",
            "http://127.0.0.1:3012", "http://127.0.0.1:5173",
        ]
        allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
        
        return JSONResponse(
            status_code=401,
            headers={
                "Access-Control-Allow-Origin": allow_origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "WWW-Authenticate": "Bearer",
            },
            content={
                "detail": "无法验证凭据，请先登录"
            }
        )
    
    # 其他验证错误，返回 422
    origin = request.headers.get("Origin")
    allowed_origins = [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
        "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
        "http://localhost:3006", "http://localhost:3007", "http://localhost:3008",
        "http://localhost:3009", "http://localhost:3010", "http://localhost:3011",
        "http://localhost:3012", "http://localhost:5173",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
        "http://127.0.0.1:3003", "http://127.0.0.1:3004", "http://127.0.0.1:3005",
        "http://127.0.0.1:3006", "http://127.0.0.1:3007", "http://127.0.0.1:3008",
        "http://127.0.0.1:3009", "http://127.0.0.1:3010", "http://127.0.0.1:3011",
        "http://127.0.0.1:3012", "http://127.0.0.1:5173",
    ]
    allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
    
    return JSONResponse(
        status_code=422,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        content={
            "detail": errors
        }
    )

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，用于捕获和记录所有未处理的异常"""
    # 如果是OPTIONS请求，直接返回200（CORS预检请求）
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        allowed_origins = [
            "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
            "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
            "http://localhost:3006", "http://localhost:3007", "http://localhost:3008",
            "http://localhost:3009", "http://localhost:3010", "http://localhost:3011",
            "http://localhost:3012", "http://localhost:5173",
            "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
            "http://127.0.0.1:3003", "http://127.0.0.1:3004", "http://127.0.0.1:3005",
            "http://127.0.0.1:3006", "http://127.0.0.1:3007", "http://127.0.0.1:3008",
            "http://127.0.0.1:3009", "http://127.0.0.1:3010", "http://127.0.0.1:3011",
            "http://127.0.0.1:3012", "http://127.0.0.1:5173",
        ]
        allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": allow_origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            },
            content={}
        )
    
    import traceback
    error_trace = traceback.format_exc()
    print(f"Unhandled exception: {error_trace}")
    
    # 获取请求的Origin头并设置CORS头
    origin = request.headers.get("Origin")
    allowed_origins = [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
        "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
        "http://localhost:3006", "http://localhost:3007", "http://localhost:3008",
        "http://localhost:3009", "http://localhost:3010", "http://localhost:3011",
        "http://localhost:3012", "http://localhost:5173",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002",
        "http://127.0.0.1:3003", "http://127.0.0.1:3004", "http://127.0.0.1:3005",
        "http://127.0.0.1:3006", "http://127.0.0.1:3007", "http://127.0.0.1:3008",
        "http://127.0.0.1:3009", "http://127.0.0.1:3010", "http://127.0.0.1:3011",
        "http://127.0.0.1:3012", "http://127.0.0.1:5173",
    ]
    allow_origin = origin if origin in allowed_origins else allowed_origins[0] if allowed_origins else "*"
    
    return JSONResponse(
        status_code=500,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": error_trace
        }
    )

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(counselors.router, prefix="/api/counselors", tags=["咨询师"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["预约"])
app.include_router(tests.router, prefix="/api/tests", tags=["心理测评"])
app.include_router(content.router, prefix="/api/content", tags=["健康科普"])
app.include_router(community.router, prefix="/api/community", tags=["互助社区"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])


@app.get("/")
async def root():
    """根路径 - API 健康检查"""
    return {
        "message": "南湖心理咨询管理平台 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    # 启动服务器
    # 运行命令: python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式热重载
        log_level="info"
    )
