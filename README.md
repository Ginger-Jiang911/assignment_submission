# 作业提交系统 (Assignment Submission System)

一个基于Django的作业提交与管理系统，为教师和学生提供便捷的作业提交、评阅和管理功能。

## 📋 项目概述

该系统是一个功能完整的在线作业管理平台，支持：
- 📤 学生作业提交与版本管理
- 👨‍🏫 教师后台管理与数据统计
- 🔄 自动文件重命名与组织
- 💾 多种存储后端支持
- 📊 完整的数据导出功能
- 🔐 用户认证与权限管理

## 🚀 核心功能

### 学生功能
- **作业浏览** - 查看所有可用的作业项目
- **文件提交** - 支持上传各种格式的作业文件
- **提交管理** - 查看提交历史和提交状态
- **申诉机制** - 对提交结果进行申诉
- **截止时间提醒** - 项目截止状态实时显示

### 管理员功能
- **项目管理** - 创建、编辑和管理作业项目
- **用户管理** - 管理学生和管理员账户
- **提交审查** - 查看和下载所有学生提交
- **自动重命名** - 灵活的文件重命名规则配置
- **数据统计** - 生成提交统计报表
- **系统设置** - 配置存储后端、备份策略等
- **数据导出** - 导出项目列表、提交记录等

## 🏗️ 项目结构

```
assignment_submission/
├── accounts/              # 用户认证与管理
│   ├── models.py         # 自定义User模型
│   ├── views.py          # 登录、注册视图
│   ├── forms.py          # 认证表单
│   └── urls.py           # 用户相关路由
├── assignments/          # 作业核心功能
│   ├── models.py         # Project、Submission模型
│   ├── views.py          # 作业提交逻辑
│   ├── admin.py          # Django后台配置
│   └── management/       # 自定义管理命令
├── admin_panel/          # 管理员面板
│   ├── views.py          # 仪表盘、设置、统计
│   ├── admin.py          # 后台管理配置
│   └── urls.py           # 管理面板路由
├── config/               # Django项目配置
│   ├── settings.py       # 项目设置
│   ├── urls.py           # URL主路由
│   └── wsgi.py           # WSGI配置
├── templates/            # HTML模板
│   ├── base.html         # 基础模板
│   ├── accounts/         # 认证相关模板
│   ├── assignments/      # 作业相关模板
│   └── admin_panel/      # 管理面板模板
├── static/               # 静态资源
│   ├── css/             # 样式文件
│   └── js/              # JavaScript脚本
├── media/               # 用户上传的文件
└── manage.py            # Django管理脚本
```

## 📦 数据模型

### User 用户模型
```
- student_id      学号 (unique)
- name            姓名
- is_active       是否激活
- is_staff        是否为员工（教师）
- is_admin        是否为超级管理员
- created_at      注册时间
```

### Project 项目模型
```
- name                 项目名称
- slug                 URL标识符 (unique)
- description          项目描述
- is_active            是否启用
- auto_rename          是否启用自动重命名
- rename_pattern       重命名规则模板
- storage_backend      存储后端 (local/webdav/s3/smb)
- deadline             截止时间
- max_file_size        最大文件大小 (MB)
- allowed_extensions   允许的文件类型
- created_at           创建时间
```

### Submission 提交模型
```
- project              关联项目
- student              关联学生
- file                 上传文件
- original_filename    原始文件名
- renamed_filename     重命名后文件名
- file_size            文件大小 (bytes)
- auto_renamed         是否自动重命名
- appeal               申诉内容
- appeal_submitted     是否已提交申诉
- submitted_at         提交时间
```

## 🔧 环境配置

### 系统要求
- Python 3.8+
- Django 6.0+
- SQLite 3 或其他数据库

### 依赖安装

```bash
# 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate
# 或 Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 依赖包
```
Django==6.0.7                    # Web框架
django-crispy-forms==2.6         # 表单美化
crispy-bootstrap5==2026.3        # Bootstrap 5集成
```

## 🚀 快速开始

### 1. 数据库初始化
```bash
python manage.py migrate
```

### 2. 创建超级管理员
```bash
python manage.py createsuperuser
```

### 3. 收集静态文件
```bash
python manage.py collectstatic --noinput
```

### 4. 运行开发服务器
```bash
python manage.py runserver
```

访问：
- 学生页面：http://localhost:8000/
- 管理后台：http://localhost:8000/admin/
- 管理面板：http://localhost:8000/admin-panel/

## 🔐 用户指南

### 学生流程
1. **注册** - 使用学号和姓名注册账户
2. **登录** - 登录到学生首页
3. **浏览项目** - 查看所有可用的作业项目
4. **提交作业** - 选择项目并上传文件
5. **查看状态** - 查看提交状态和截止时间

### 教师/管理员流程
1. **登录** - 使用管理员账户登录
2. **创建项目** - 在后台创建新的作业项目
3. **配置项目** - 设置截止时间、文件大小限制、允许的文件类型等
4. **配置重命名** - 设置自动重命名规则模板
5. **监控提交** - 在管理面板查看提交情况
6. **导出数据** - 下载提交记录和统计数据
7. **系统维护** - 配置存储后端和备份策略

## ⚙️ 高级配置

### 文件重命名模板变量
在项目的重命名规则中，可以使用以下变量：
```
{student_id}    - 学号
{name}         - 学生姓名
{project}      - 项目名称
{timestamp}    - 提交时间戳 (YYYYMMDD_HHMMSS格式)
{original_name} - 原始文件名（不含扩展名）
{ext}          - 文件扩展名
```

**示例：**
- `{student_id}_{name}_{timestamp}{ext}` → `20230001_张三_20231215_093045.pdf`
- `{project}_{student_id}{ext}` → `Python作业_20230001.docx`

### 存储后端配置

系统支持多种存储后端，可在管理面板中配置：
- **本地存储** (local) - 保存在服务器本地
- **WebDAV** - 连接到WebDAV服务器
- **Amazon S3** - 云存储服务
- **SMB共享** - 连接到Windows共享文件夹

### 系统设置
在管理面板的"系统设置"页面可以配置：
- 各个存储后端的连接参数
- 自动备份策略和间隔
- 自动清理过期提交的设置

## 📊 管理命令

### 备份和清理
```bash
python manage.py backup_and_cleanup
```
执行定期备份和清理过期提交的任务。

## 🔒 安全性说明

⚠️ **开发环境注意事项**：
- `DEBUG = True` 仅用于开发，生产环境应设置为 `False`
- `SECRET_KEY` 应该更改为强密钥
- `ALLOWED_HOSTS = ["*"]` 在生产环境中应限制为特定域名

## 📝 许可证

本项目为开源项目。

## 🤝 贡献

欢迎提交问题报告和改进建议。

## 📧 技术支持

如有问题，请提交Issue或联系项目维护者。