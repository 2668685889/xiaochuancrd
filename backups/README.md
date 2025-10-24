# 小川ERP系统备份

## 备份信息
- **备份时间**: 2025-10-24 09:35:37
- **备份版本**: 开发新复杂功能前的完整备份
- **备份范围**: 整个小川ERP项目目录

## 项目状态
此备份包含以下主要功能：
- 进销存管理系统前端（React + TypeScript + Tailwind CSS）
- 后端API服务（FastAPI + SQLAlchemy）
- MCP MySQL服务（智能查询助手）
- 数据库模型和迁移文件
- 完整的项目配置和依赖

## 恢复方法
如需从此备份恢复项目，请执行以下步骤：

1. 停止当前运行的服务
   ```bash
   cd /Users/hui/trae/xiaochuanerp
   ./stop.sh
   ```

2. 备份当前项目（可选）
   ```bash
   cp -r /Users/hui/trae/xiaochuanerp /Users/hui/trae/xiaochuanerp_current_$(date +%Y%m%d_%H%M%S)
   ```

3. 恢复项目文件
   ```bash
   rm -rf /Users/hui/trae/xiaochuanerp/*
   cp -r /Users/hui/trae/xiaochuanerp/backups/xiaochuanerp_backup_20251024_093537/* /Users/hui/trae/xiaochuanerp/
   ```

4. 重新启动服务
   ```bash
   cd /Users/hui/trae/xiaochuanerp
   ./start.sh
   ```

## 注意事项
- 此备份不包含数据库数据，仅包含代码和配置文件
- 如需恢复数据库，请使用相应的数据库备份文件
- 恢复后可能需要重新安装依赖和配置环境变量