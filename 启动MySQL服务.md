# 如何启动 MySQL 服务

## ❌ 错误：拒绝访问 / 系统错误 5

如果你遇到以下错误：
```
发生系统错误 5。
拒绝访问。
```

这表示你**没有管理员权限**来启动 Windows 服务。

---

## ✅ 解决方案（3 种方法）

### 方法 1: 通过服务管理器（最简单，推荐）

**优点：不需要管理员权限，图形界面操作**

1. 按 `Win + R` 键
2. 输入 `services.msc` 并回车
3. 在服务列表中找到 MySQL 服务：
   - 滚动查找 `mysql57`，或
   - 滚动查找 `phpStudyMySQL57`
4. **右键点击服务** → 选择 **"启动"**
5. 等待 5-10 秒，服务状态会从"已停止"变为"正在运行"

**如果找不到服务：**
- 在服务列表顶部，按 `Ctrl + F` 搜索 "mysql"
- 或者在服务列表顶部，按 `M` 键快速跳转到 M 开头的服务

---

### 方法 2: 以管理员身份运行 PowerShell

**优点：命令行操作，适合熟悉命令行的用户**

1. **关闭当前的 PowerShell 窗口**

2. **以管理员身份打开 PowerShell：**
   - 按 `Win` 键
   - 输入 `powershell` 或 `PowerShell`
   - **右键点击** "Windows PowerShell"
   - 选择 **"以管理员身份运行"**
   - 在弹出的 UAC 对话框中点击 **"是"**

3. **在管理员 PowerShell 中执行：**
   ```powershell
   # 尝试启动 mysql57
   net start mysql57
   
   # 如果上面失败，尝试启动 phpStudyMySQL57
   net start phpStudyMySQL57
   ```

4. **验证服务是否启动：**
   ```powershell
   Get-Service -Name "*mysql*" | Select-Object Name, Status
   ```
   应该看到状态为 `Running`

---

### 方法 3: 使用批处理脚本（便捷）

**优点：一键启动，适合经常使用**

1. **找到项目根目录的 `start_mysql.bat` 文件**

2. **右键点击 `start_mysql.bat`**

3. **选择 "以管理员身份运行"**

4. **在弹出的 UAC 对话框中点击 "是"**

5. **脚本会自动：**
   - 检查哪些 MySQL 服务可用
   - 启动找到的服务
   - 显示启动结果

---

## 🔍 验证 MySQL 是否已启动

启动服务后，运行以下命令验证：

```powershell
cd D:\PycharmProjects\heart-care\src\backend
python check_mysql_connection.py
```

如果看到 `[SUCCESS] 所有检查通过！MySQL 连接正常`，说明成功了！

---

## 📝 设置 MySQL 自动启动（推荐）

为了避免每次都要手动启动，建议设置 MySQL 服务为自动启动：

1. 打开服务管理器（`Win + R` → `services.msc`）
2. 找到 MySQL 服务（`mysql57` 或 `phpStudyMySQL57`）
3. **右键点击服务** → 选择 **"属性"**
4. 在"启动类型"下拉菜单中选择 **"自动"**
5. 点击 **"确定"**

这样，下次开机时 MySQL 会自动启动，不需要手动操作。

---

## ❓ 常见问题

### Q: 服务启动失败，提示"服务无法启动"

**可能原因：**
- MySQL 配置文件有错误
- MySQL 数据目录权限问题
- 端口被占用

**解决方法：**
1. 查看服务属性中的错误信息
2. 检查 MySQL 错误日志（通常在 MySQL 安装目录的 `data` 文件夹中）
3. 尝试重启电脑后再启动服务

### Q: 找不到 MySQL 服务

**可能原因：**
- MySQL 没有安装为 Windows 服务
- 使用的是 phpStudy，但 MySQL 不是服务形式

**解决方法：**
1. 如果使用 phpStudy，请从 phpStudy 控制面板启动 MySQL
2. 或者重新安装 MySQL 并选择安装为 Windows 服务

### Q: 服务启动成功，但仍然无法连接

**解决方法：**
1. 运行诊断脚本：`python src/backend/check_mysql_connection.py`
2. 检查用户名和密码是否正确
3. 检查数据库是否存在

---

## 🎯 快速操作步骤总结

1. **最简单方法**：`Win + R` → 输入 `services.msc` → 找到 MySQL 服务 → 右键启动
2. **命令行方法**：以管理员身份打开 PowerShell → 运行 `net start mysql57`
3. **脚本方法**：右键 `start_mysql.bat` → 以管理员身份运行

选择最适合你的方法即可！






