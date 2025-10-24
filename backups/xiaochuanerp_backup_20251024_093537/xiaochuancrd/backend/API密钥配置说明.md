# API密钥配置说明

## 🔐 安全配置原则

本项目采用**环境变量**方式管理API密钥，确保：
- ✅ **密钥不硬编码**在源代码中
- ✅ **支持多人协作**，每个人使用自己的密钥
- ✅ **密钥过期时**只需更新环境变量，无需修改代码
- ✅ **部署到不同环境**时使用不同的密钥

## 📋 配置步骤

### 1. 复制配置文件模板

```bash
# 复制主应用配置文件
cp .env.example .env

# 复制MCP服务专用配置文件
cp .env.example .env.mcp
```

### 2. 配置API密钥

编辑 `.env` 文件，填入您的实际API密钥：

```bash
# API密钥配置（必须配置）
DEEPSEEK_API_KEY=您的DeepSeek_API密钥
DEEPSEEK_API_KEY_MCP=您的DeepSeek_MCP专用密钥
COZE_API_KEY=您的Coze_API密钥
```

编辑 `.env.mcp` 文件，配置MCP服务专用密钥：

```bash
# MCP服务专用配置
DEEPSEEK_API_KEY=您的DeepSeek_MCP专用密钥
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 重启服务

```bash
# 停止当前服务
./stop.sh

# 重新启动服务
./start.sh
```

## 🔧 密钥获取方式

### DeepSeek API密钥
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥到配置文件中

### Coze API密钥
1. 访问 [Coze官网](https://www.coze.cn/)
2. 注册账号并登录
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥到配置文件中

## 🚀 部署到不同环境

### 开发环境
- 使用开发环境的API密钥
- 配置在 `.env` 文件中

### 测试环境
- 使用测试环境的API密钥
- 配置在 `.env.test` 文件中

### 生产环境
- 使用生产环境的API密钥
- 配置在服务器环境变量中
- **不要**将生产密钥提交到代码仓库

## 🔒 安全最佳实践

1. **不要提交 `.env` 文件到Git**
   ```bash
   # 确保 .env 在 .gitignore 中
   echo ".env" >> .gitignore
   echo ".env.mcp" >> .gitignore
   ```

2. **定期轮换密钥**
   - 定期更新API密钥
   - 旧密钥过期前创建新密钥
   - 平滑过渡，避免服务中断

3. **使用密钥管理服务**
   - 生产环境建议使用AWS Secrets Manager、Azure Key Vault等
   - 开发环境使用环境变量文件

## ❌ 常见问题

### Q: 为什么API密钥要分开配置？
A: MCP服务需要独立的API密钥配置，确保服务间的隔离性和安全性。

### Q: 密钥过期了怎么办？
A: 只需更新 `.env` 和 `.env.mcp` 文件中的密钥值，然后重启服务即可。

### Q: 多人协作时如何管理密钥？
A: 每个人创建自己的 `.env` 文件，使用各自的API密钥。

## 📞 技术支持

如遇配置问题，请检查：
1. API密钥是否正确
2. 环境变量文件路径是否正确
3. 服务是否已重启
4. 查看日志文件中的错误信息

---

**注意：请妥善保管您的API密钥，不要泄露给他人！**