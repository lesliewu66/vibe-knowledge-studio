# 定位工具与运行环境

项目内 Skill 的根目录向上三级即工具根目录，包含 `studio.py`、`engine/` 和 `requirements.txt`。

推荐使用根目录 `.venv/bin/python`（Windows 为 `.venv\Scripts\python`）。如果由其他虚拟环境驱动，先执行 `studio.py doctor` 验证依赖。

全局安装 Skill 时，不应假设工具也随 Skill 复制；在当前项目或用户指定位置查找工具根目录。缺失时按 README 安装完整仓库，不要伪造已存在的路径。
