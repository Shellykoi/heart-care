@echo off
REM MySQL 服务启动脚本
REM 需要以管理员身份运行

echo ========================================
echo MySQL 服务启动脚本
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] 此脚本需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [INFO] 正在检查 MySQL 服务...
echo.

REM 检查 mysql57 服务
sc query mysql57 >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] 找到服务: mysql57
    sc query mysql57 | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] mysql57 服务已在运行
    ) else (
        echo [INFO] 正在启动 mysql57...
        net start mysql57
        if %errorLevel% equ 0 (
            echo [OK] mysql57 服务已成功启动
        ) else (
            echo [ERROR] mysql57 服务启动失败
        )
    )
    echo.
)

REM 检查 phpStudyMySQL57 服务
sc query phpStudyMySQL57 >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] 找到服务: phpStudyMySQL57
    sc query phpStudyMySQL57 | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] phpStudyMySQL57 服务已在运行
    ) else (
        echo [INFO] 正在启动 phpStudyMySQL57...
        net start phpStudyMySQL57
        if %errorLevel% equ 0 (
            echo [OK] phpStudyMySQL57 服务已成功启动
        ) else (
            echo [ERROR] phpStudyMySQL57 服务启动失败
        )
    )
    echo.
)

echo ========================================
echo 启动完成
echo ========================================
echo.
echo 如果服务启动成功，现在可以运行数据库迁移了：
echo   cd src/backend
echo   python -m alembic upgrade head
echo.
pause






