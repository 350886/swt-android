# SWT 货运管理系统 (Sum Wah Transport)

## 项目概述

基于 Python Tkinter 的货运管理系统，包含客户、司机、关键词管理等功能。

## 项目结构

```
agent-web-app/
├── swt_system/           # 重构后的 Python 模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接池
│   ├── utils.py          # 日志工具
│   └── gui/
│       └── base.py       # GUI 基类
├── swt_system_javafx/   # JavaFX 版本
├── swt-android-app/     # Android 版本 (Kotlin)
├── swt_management_system.py  # 原始 Python 代码
├── main.py              # Python GUI 入口
└── requirements.txt     # Python 依赖
```

## 开发环境

### Python 版本
- Python 3.8+

### 依赖
```bash
pip install -r requirements.txt
```

### 运行 Python GUI
```bash
python main.py
```

### Android 开发
- JDK 21
- Android SDK (platform-34)
- Gradle 8.5

### 构建 Android APK
```bash
cd swt-android-app
gradle assembleDebug
```

APK 输出路径: `app/build/outputs/apk/debug/app-debug.apk`

## 功能模块

1. **关键词管理** - 搜索关键词配置
2. **客户管理** - 客户信息维护
3. **司机管理** - 司机信息维护
4. **统计数据** - 业务数据统计
5. **系统设置** - 应用配置
