# MySQL 连接错误 10061 解决方案

## 错误信息
```
(pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost' ([WinError 10061] 由于目标计算机积极拒绝，无法连接。)")
```

## 问题原因

**错误代码 10061** 表示"目标计算机积极拒绝连接"，通常有以下原因：

1. **MySQL 服务未启动**（最常见）
2. MySQL 服务未监听在 localhost:3306
3. 防火墙阻止了连接
4. MySQL 配置不允许本地连接

## 解决方案

### 方法 1: 通过服务管理器启动 MySQL（推荐，无需管理员权限）

**这是最简单的方法，不需要管理员权限！**

1. 按 `Win + R` 打开运行对话框
2. 输入 `services.msc` 并回车
3. 在服务列表中找到 MySQL 服务：
   - 查找 `mysql57` 或 
   - 查找 `phpStudyMySQL57`
4. **右键点击服务** → 选择 **"启动"**
5. 等待几秒钟，服务状态会从"已停止"变为"正在运行"
6. 如果服务启动失败，查看错误信息（双击服务可以查看详细信息）

### 方法 2: 使用命令行启动（需要管理员权限）

```powershell
# 以管理员身份运行 PowerShell，然后执行：

# 启动 mysql57 服务
net start mysql57

# 或启动 phpStudyMySQL57 服务
net start phpStudyMySQL57

# 或使用 sc 命令
sc start mysql57
```

### 方法 3: 如果使用 phpStudy

1. 打开 phpStudy 控制面板
2. 在 MySQL 服务旁边点击"启动"按钮
3. 等待服务启动完成

### 方法 4: 检查 MySQL 是否在其他端口运行

如果 MySQL 服务在其他端口运行，需要修改 `src/backend/database.py` 中的端口号：

```python
DATABASE_URL = "mysql+pymysql://shellykoi:123456koiii@localhost:3307/heart_care"
# 注意：将 3306 改为实际端口号（如 3307）
```

### 方法 5: 检查防火墙设置

1. 打开 Windows 防火墙设置
2. 确保 MySQL 端口（默认 3306）没有被阻止
3. 临时关闭防火墙测试（仅用于诊断）

## 诊断步骤

### 步骤 1: 运行诊断脚本

```bash
cd src/backend
python check_mysql_connection.py
```

这个脚本会：
- 检查 pymysql 是否安装
- 尝试连接 MySQL 服务器
- 检查数据库是否存在
- 提供详细的错误信息和建议

### 步骤 2: 手动测试连接

```powershell
# 测试 MySQL 端口是否开放
Test-NetConnection -ComputerName localhost -Port 3306
```

如果显示 "TcpTestSucceeded: False"，说明 MySQL 服务未运行或端口未监听。

### 步骤 3: 检查服务状态

```powershell
Get-Service -Name "*mysql*"
```

查看服务状态，如果是 "Stopped"，需要启动服务。

## 常见问题

### Q1: 服务启动失败，提示"无法启动服务"

**可能原因：**
- MySQL 配置文件有错误
- MySQL 数据目录权限问题
- 端口被占用

**解决方法：**
1. 检查 MySQL 错误日志（通常在 MySQL 安装目录的 `data` 文件夹中）
2. 查看 Windows 事件查看器中的错误信息
3. 尝试重新安装 MySQL 或使用 MySQL 官方安装包

### Q2: 服务启动成功，但仍然无法连接

**可能原因：**
- 用户名或密码错误
- 数据库不存在
- 用户没有权限

**解决方法：**
1. 运行诊断脚本检查详细信息
2. 使用 MySQL 客户端（如 MySQL Workbench）测试连接
3. 检查 `database.py` 中的配置是否正确

### Q3: 使用 phpStudy，但找不到 MySQL 服务

**解决方法：**
1. phpStudy 的 MySQL 可能不是 Windows 服务形式运行
2. 确保从 phpStudy 控制面板启动 MySQL
3. 检查 phpStudy 的 MySQL 端口配置

## 验证连接

启动 MySQL 服务后，运行以下命令验证：

```bash
cd src/backend
python check_mysql_connection.py
```

如果一切正常，应该看到：
```
✓ 成功连接到 MySQL 服务器
✓ 数据库存在
✓ 成功连接到数据库
✓ 所有检查通过！MySQL 连接正常
```

## 预防措施

1. **设置 MySQL 服务自动启动**
   - 在服务管理器中，右键 MySQL 服务
   - 选择"属性"
   - 将"启动类型"设置为"自动"

2. **创建启动脚本**
   - 创建一个批处理文件，在运行项目前自动启动 MySQL
   - 例如：`start_mysql.bat`

3. **使用数据库连接池**
   - 项目已经配置了连接池，可以自动重试连接
   - 但前提是 MySQL 服务必须运行

## 联系支持

如果以上方法都无法解决问题，请：
1. 运行诊断脚本并保存输出
2. 查看 MySQL 错误日志
3. 检查 Windows 事件查看器
4. 提供详细的错误信息

