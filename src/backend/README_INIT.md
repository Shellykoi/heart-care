# 数据库初始化说明

## 初始化数据库

运行以下命令来初始化数据库（创建数据库、创建表结构、清空所有数据）：

```bash
cd src/backend
python init_db.py
```

## 配置说明

数据库连接配置在 `database.py` 中：

```python
DATABASE_URL = "mysql+pymysql://shellykoi:123456koiii@localhost:3306/nanhu_psychology"
```

请确保：
1. MySQL 服务已启动
2. 数据库用户 `shellykoi` 存在且有权限
3. 如果数据库不存在，脚本会自动创建

## 启动后端服务

```bash
cd src/backend
python main.py
```

或者使用 uvicorn：

```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 注意事项

1. 首次运行 `init_db.py` 会创建数据库和所有表
2. 如果表已存在，会先删除再创建（**这会清空所有数据**）
3. 初始化完成后，数据库为空，需要从注册第一个用户开始





