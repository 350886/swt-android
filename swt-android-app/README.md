# SWT Android App (Kivy 版本)

## 项目结构

```
swt-android-app/
├── main.py              # 主应用入口
├── screens/             # 各功能页面
│   ├── __init__.py
│   ├── keyword.py       # 检测关键字
│   ├── customer.py      # 客户管理
│   ├── driver.py        # 司机管理
│   ├── stats.py         # 公司统计
│   └── settings.py      # 系统设置
├── buildozer.spec       # Buildozer 构建配置
└── README.md            # 本说明
```

## 功能特性

1. **检测关键字** - 月度检查、规则管理（增删改）
2. **客户管理** - 客户月结单导出、客户汇总表导出
3. **司机管理** - 司机列表查看、司机统计导出
4. **公司统计** - 统计概览、客户/司机月度汇总导出
5. **系统设置** - 数据库连接配置、导出目录设置

## 构建 APK

由于 Kivy/Buildozer 需要 Linux 环境，推荐使用 **Google Colab** 构建：

### 快速开始

1. 打开 https://colab.research.google.com 新建笔记本

2. 上传项目文件：
   ```python
   from google.colab import files
   uploaded = files.upload()
   ```
   上传 `swt-android-app/` 整个文件夹

3. 运行构建命令：
   ```python
   !pip install buildozer cython
   !apt install -y git zip unzip openjdk-17-jdk
   %cd swt-android-app
   !buildozer android debug
   ```

4. 下载 APK：`bin/` 目录下

### 本地构建 (Linux/WSL)

```bash
# 安装依赖
sudo apt install -y python3-pip openjdk-17-jdk git
pip install buildozer cython kivy

# 进入项目目录
cd swt-android-app

# 初始化（已配置可跳过）
buildozer init

# 构建 Debug APK
buildozer android debug
```

## 注意事项

- 数据库连接需要能访问 MySQL 服务器（同一网络或VPN）
- 导出文件保存到 Android 设备的 Downloads 目录
- 首次使用需在"设置"中配置数据库连接参数