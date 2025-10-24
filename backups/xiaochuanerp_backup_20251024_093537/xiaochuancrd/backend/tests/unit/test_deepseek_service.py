"""
DeepSeek服务单元测试
测试多轮对话功能
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.deepseek_service import DeepSeekService, ConversationManager, ConversationMessage


class TestConversationMessage:
    """对话消息测试类"""
    
    def test_conversation_message_creation(self):
        """测试对话消息创建"""
        message = ConversationMessage("user", "你好")
        
        assert message.role == "user"
        assert message.content == "你好"
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_conversation_message_to_dict(self):
        """测试对话消息转换为字典"""
        message = ConversationMessage("assistant", "你好，我是助手")
        
        result = message.to_dict()
        
        assert result == {
            "role": "assistant",
            "content": "你好，我是助手"
        }


class TestConversationManager:
    """对话管理器测试类"""
    
    @pytest.fixture
    def conversation_manager(self):
        """对话管理器fixture"""
        return ConversationManager(max_history=5)
    
    def test_conversation_manager_initialization(self, conversation_manager):
        """测试对话管理器初始化"""
        assert conversation_manager.max_history == 5
        assert conversation_manager.conversations == {}
    
    def test_start_conversation(self, conversation_manager):
        """测试开始对话"""
        conversation_manager.start_conversation("test-conv-1")
        
        assert "test-conv-1" in conversation_manager.conversations
        assert conversation_manager.conversations["test-conv-1"] == []
    
    def test_start_conversation_with_system_prompt(self, conversation_manager):
        """测试带系统提示词的开始对话"""
        conversation_manager.start_conversation("test-conv-2", "你是一个助手")
        
        assert "test-conv-2" in conversation_manager.conversations
        assert len(conversation_manager.conversations["test-conv-2"]) == 1
        assert conversation_manager.conversations["test-conv-2"][0].role == "system"
        assert conversation_manager.conversations["test-conv-2"][0].content == "你是一个助手"
    
    def test_add_message(self, conversation_manager):
        """测试添加消息"""
        conversation_manager.add_message("test-conv-3", "user", "第一条消息")
        
        assert "test-conv-3" in conversation_manager.conversations
        assert len(conversation_manager.conversations["test-conv-3"]) == 1
        assert conversation_manager.conversations["test-conv-3"][0].role == "user"
        assert conversation_manager.conversations["test-conv-3"][0].content == "第一条消息"
    
    def test_add_message_to_existing_conversation(self, conversation_manager):
        """测试向已存在的对话添加消息"""
        conversation_manager.start_conversation("test-conv-4")
        conversation_manager.add_message("test-conv-4", "user", "用户消息")
        conversation_manager.add_message("test-conv-4", "assistant", "助手回复")
        
        assert len(conversation_manager.conversations["test-conv-4"]) == 2
        assert conversation_manager.conversations["test-conv-4"][0].role == "user"
        assert conversation_manager.conversations["test-conv-4"][1].role == "assistant"
    
    def test_get_messages(self, conversation_manager):
        """测试获取消息列表"""
        conversation_manager.add_message("test-conv-5", "user", "测试消息")
        
        messages = conversation_manager.get_messages("test-conv-5")
        
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": "测试消息"}
    
    def test_get_messages_nonexistent_conversation(self, conversation_manager):
        """测试获取不存在的对话的消息"""
        messages = conversation_manager.get_messages("nonexistent")
        
        assert messages == []
    
    def test_clear_conversation(self, conversation_manager):
        """测试清空对话"""
        conversation_manager.add_message("test-conv-6", "user", "消息1")
        conversation_manager.add_message("test-conv-6", "assistant", "回复1")
        
        conversation_manager.clear_conversation("test-conv-6")
        
        assert "test-conv-6" in conversation_manager.conversations
        assert conversation_manager.conversations["test-conv-6"] == []
    
    def test_end_conversation(self, conversation_manager):
        """测试结束对话"""
        conversation_manager.add_message("test-conv-7", "user", "消息")
        
        conversation_manager.end_conversation("test-conv-7")
        
        assert "test-conv-7" not in conversation_manager.conversations
    
    def test_history_limit(self, conversation_manager):
        """测试对话历史限制"""
        # 添加超过限制的消息
        for i in range(10):
            conversation_manager.add_message("test-conv-8", "user", f"消息{i}")
        
        messages = conversation_manager.get_messages("test-conv-8")
        
        # 应该限制在最大历史长度内
        assert len(messages) <= 5


class TestDeepSeekService:
    """DeepSeek服务测试类"""
    
    @pytest.fixture
    def deepseek_service(self):
        """DeepSeek服务fixture"""
        return DeepSeekService(api_key="test-key", base_url="https://api.test.com/v1")
    
    @pytest.fixture
    def mock_api_response(self):
        """模拟API响应"""
        return {
            "choices": [{
                "message": {
                    "content": "这是AI的回复"
                }
            }],
            "usage": {
                "total_tokens": 100
            }
        }
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, deepseek_service):
        """测试服务初始化成功"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            await deepseek_service.initialize()
            
            assert deepseek_service.is_initialized == True
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self, deepseek_service):
        """测试服务初始化失败"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_client.get.return_value = mock_response
            
            await deepseek_service.initialize()
            
            assert deepseek_service.is_initialized == False
    
    @pytest.mark.asyncio
    async def test_is_ready_success(self, deepseek_service):
        """测试服务就绪检查成功"""
        # 先初始化服务
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            await deepseek_service.initialize()
            
            result = await deepseek_service.is_ready()
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_is_ready_not_initialized(self, deepseek_service):
        """测试服务未初始化时的就绪检查"""
        result = await deepseek_service.is_ready()
        
        assert result == False
    
    @pytest.mark.asyncio
    async def test_generate_response_single_turn(self, deepseek_service, mock_api_response):
        """测试单轮对话响应生成"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            result = await deepseek_service.generate_response("你好")
            
            assert result["success"] == True
            assert result["response"] == "这是AI的回复"
            assert result["model"] == "deepseek-chat"
            assert result["tokens_used"] == 100
    
    @pytest.mark.asyncio
    async def test_generate_response_multi_turn(self, deepseek_service, mock_api_response):
        """测试多轮对话响应生成"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            # 第一轮对话
            result1 = await deepseek_service.generate_response(
                "查询产品库存",
                conversation_id="test-conv-1"
            )
            
            # 第二轮对话（应该包含历史）
            result2 = await deepseek_service.generate_response(
                "再查询一下销售订单",
                conversation_id="test-conv-1"
            )
            
            assert result1["success"] == True
            assert result2["success"] == True
            assert result1["conversation_id"] == "test-conv-1"
            assert result2["conversation_id"] == "test-conv-1"
            
            # 验证对话历史
            history = deepseek_service.get_conversation_history("test-conv-1")
            assert len(history) == 5  # system + user1 + assistant1 + user2 + assistant2
    
    @pytest.mark.asyncio
    async def test_generate_response_with_system_prompt(self, deepseek_service, mock_api_response):
        """测试带系统提示词的响应生成"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            result = await deepseek_service.generate_response(
                "查询数据",
                conversation_id="test-conv-2",
                system_prompt="你是一个ERP系统助手"
            )
            
            assert result["success"] == True
            
            # 验证系统提示词被正确设置
            history = deepseek_service.get_conversation_history("test-conv-2")
            assert len(history) == 3  # system + user + assistant
            assert history[0]["role"] == "system"
            assert history[0]["content"] == "你是一个ERP系统助手"
    
    @pytest.mark.asyncio
    async def test_generate_response_api_error(self, deepseek_service):
        """测试API错误处理"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API错误响应
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            result = await deepseek_service.generate_response("测试消息")
            
            assert result["success"] == False
            assert "API请求失败" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_multi_turn_response(self, deepseek_service, mock_api_response):
        """测试多轮对话响应生成（专用方法）"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            result = await deepseek_service.generate_multi_turn_response(
                conversation_id="test-conv-3",
                message="查询产品信息",
                system_prompt="ERP助手"
            )
            
            assert result["success"] == True
            assert result["conversation_id"] == "test-conv-3"
    
    @pytest.mark.asyncio
    async def test_clear_conversation_history(self, deepseek_service):
        """测试清空对话历史"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "回复"}}]}
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            # 先创建对话
            await deepseek_service.generate_response(
                "消息1",
                conversation_id="test-conv-4"
            )
            
            # 验证对话历史存在
            history_before = deepseek_service.get_conversation_history("test-conv-4")
            assert len(history_before) > 0
            
            # 清空对话历史
            deepseek_service.clear_conversation_history("test-conv-4")
            
            # 验证对话历史被清空
            history_after = deepseek_service.get_conversation_history("test-conv-4")
            assert len(history_after) == 0
    
    @pytest.mark.asyncio
    async def test_end_conversation(self, deepseek_service):
        """测试结束对话"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化成功
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 200
            mock_client.get.return_value = mock_init_response
            
            # 模拟API响应
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "回复"}}]}
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # 先初始化服务
            await deepseek_service.initialize()
            
            # 先创建对话
            await deepseek_service.generate_response(
                "消息1",
                conversation_id="test-conv-5"
            )
            
            # 验证对话存在
            assert "test-conv-5" in deepseek_service.conversation_manager.conversations
            
            # 结束对话
            deepseek_service.end_conversation("test-conv-5")
            
            # 验证对话被删除
            assert "test-conv-5" not in deepseek_service.conversation_manager.conversations
    
    @pytest.mark.asyncio
    async def test_generate_response_service_not_ready(self, deepseek_service):
        """测试服务未就绪时的响应生成"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化失败
            mock_init_response = AsyncMock()
            mock_init_response.status_code = 401  # 未授权错误
            mock_client.get.return_value = mock_init_response
            
            # 不调用initialize()，让服务保持未初始化状态
            
            result = await deepseek_service.generate_response("测试消息")
            
            assert result["success"] == False
            assert "服务未就绪" in result["error"]


@pytest.mark.asyncio
async def test_conversation_history_persistence():
    """测试对话历史的持久性"""
    service = DeepSeekService(api_key="test-key", base_url="https://api.test.com/v1")
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # 模拟初始化成功 - 创建一个简单的响应对象
        mock_init_response = AsyncMock()
        mock_init_response.status_code = 200
        mock_init_response.json.return_value = {"data": [{"id": "deepseek-chat"}]}
        mock_client.get = AsyncMock(return_value=mock_init_response)
        
        # 模拟API响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # 注意：json()方法应该返回一个字典，而不是设置return_value
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "回复内容"}}],
            "usage": {"total_tokens": 50}
        })
        mock_client.post = AsyncMock(return_value=mock_response)
        
        # 先初始化服务
        await service.initialize()
        
        # 创建多轮对话
        conversation_id = "persistent-conv"
        
        # 第一轮
        result1 = await service.generate_response("第一轮消息", conversation_id=conversation_id)
        history1 = service.get_conversation_history(conversation_id)
        
        # 第二轮
        result2 = await service.generate_response("第二轮消息", conversation_id=conversation_id)
        history2 = service.get_conversation_history(conversation_id)
        
        # 验证API调用成功
        assert result1["success"] == True
        assert result2["success"] == True
        
        # 验证历史正确累积
        assert len(history2) > len(history1)
        # 检查对话历史结构
        assert len(history2) >= 4  # system + user1 + assistant1 + user2 + assistant2
        assert history2[1]["content"] == "第一轮消息"  # 第一轮用户消息
        assert history2[3]["content"] == "第二轮消息"  # 第二轮用户消息


@pytest.mark.asyncio
async def test_conversation_without_history():
    """测试不使用对话历史的情况"""
    service = DeepSeekService(api_key="test-key", base_url="https://api.test.com/v1")
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # 模拟初始化成功 - 创建一个简单的响应对象
        mock_init_response = AsyncMock()
        mock_init_response.status_code = 200
        mock_init_response.json.return_value = {"data": [{"id": "deepseek-chat"}]}
        mock_client.get = AsyncMock(return_value=mock_init_response)
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # 注意：json()方法应该返回一个字典，而不是设置return_value
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "回复内容"}}],
            "usage": {"total_tokens": 50}
        })
        mock_client.post = AsyncMock(return_value=mock_response)
        
        # 先初始化服务
        await service.initialize()
        
        # 不使用对话历史
        result = await service.generate_response("测试消息", use_conversation_history=False)
        
        assert result["success"] == True
        assert result["conversation_id"] is None
        
        # 验证没有创建对话历史
        assert len(service.conversation_manager.conversations) == 0