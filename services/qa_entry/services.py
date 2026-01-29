import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
import aiohttp
import asyncio

from config import Settings
from models import ClassificationResult, ContextData

logger = logging.getLogger(__name__)

class QuestionClassifier:
    """问题分类器"""
    
    def __init__(self):
        """初始化分类器"""
        self.keywords_map = {
            "sales_inquiry": ["销售部", "销售数据", "销售额", "销售目标", "业绩", "收入", "营收", "销售量"],
            "hr_inquiry": ["员工", "人力资源", "薪资", "福利", "考勤", "招聘", "HR", "人事"],
            "technical_inquiry": ["系统", "架构", "技术", "代码", "开发", "编程", "API", "接口"],
            "financial_inquiry": ["财务", "预算", "成本", "利润", "账户", "财务报表", "收支"],
            "customer_inquiry": ["客户", "客服", "订单", "投诉", "反馈", "咨询"],
        }
    
    def classify(self, question: str) -> str:
        """
        对问题进行分类
        
        参数：
        - question: 问题文本
        
        返回：
        - question_type: 问题类型
        """
        question_lower = question.lower()
        
        # 按关键词长度排序（优先匹配长的关键词，避免误匹配）
        all_keywords = []
        for qtype, keywords in self.keywords_map.items():
            for keyword in keywords:
                all_keywords.append((len(keyword), keyword.lower(), qtype))
        
        # 按长度降序排列，这样更长的关键词会优先匹配
        all_keywords.sort(reverse=True)
        
        for length, keyword, qtype in all_keywords:
            # 使用更精确的匹配：关键词前后都是空格或标点符号
            if re.search(r'(^|\s|[，。！？])' + re.escape(keyword) + r'($|\s|[，。！？])', question_lower):
                return qtype
            # 如果上面的精确匹配失败，尝试关键词匹配（但只对于较长的关键词）
            if len(keyword) >= 3 and keyword in question_lower:
                return qtype
        
        # 默认分类
        return "general_inquiry"

class ContextBuilder:
    """上下文构建器"""
    
    def __init__(self, settings: Settings):
        """初始化构建器"""
        self.settings = settings
    
    async def build(
        self,
        question: str,
        user_id: str,
        question_type: str,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> ContextData:
        """
        构建问题处理的上下文
        
        参数：
        - question: 问题文本
        - user_id: 用户ID
        - question_type: 问题类型
        - extra_context: 额外上下文
        
        返回：
        - context: ContextData对象
        """
        context = ContextData(
            user_profile={
                "user_id": user_id,
                "question_type": question_type,
            },
            extra=extra_context or {}
        )
        
        # 从extra_context中提取部门和角色信息
        if extra_context:
            context.department = extra_context.get("department")
            context.role = extra_context.get("role")
            context.permissions = extra_context.get("permissions", [])
        
        logger.info(f"上下文构建完成 - 用户: {user_id}, 类型: {question_type}")
        
        return context

class QAProcessor:
    """QA处理器 - 协调各个服务"""
    
    def __init__(self, settings: Settings, redis):
        """初始化处理器"""
        self.settings = settings
        self.redis = redis
    
    async def process(
        self,
        question_id: str,
        question: str,
        question_type: str,
        context: ContextData,
        user_id: str
    ) -> Dict[str, Any]:
        """
        处理问题的主流程
        
        1. 检查缓存
        2. 调用RAG检索知识库
        3. 调用Agent获取实时数据
        4. 调用LLM生成答案
        5. 返回结果
        """
        
        # 1. 检查缓存
        cached_result = self._check_cache(question)
        if cached_result:
            logger.info(f"[{question_id}] 命中缓存")
            return cached_result
        
        # 2. RAG检索（模拟）
        rag_results = await self._call_rag(question, question_type)
        
        # 3. Agent调用（模拟）
        agent_results = await self._call_agent(question, question_type, context)
        
        # 4. 组装答案
        answer = await self._generate_answer(
            question=question,
            rag_results=rag_results,
            agent_results=agent_results,
            context=context
        )
        
        result = {
            "answer": answer,
            "sources": rag_results.get("sources", []) + agent_results.get("sources", []),
            "confidence": max(
                rag_results.get("confidence", 0),
                agent_results.get("confidence", 0)
            )
        }
        
        # 5. 缓存结果
        self._cache_result(question, result)
        
        return result
    
    def _check_cache(self, question: str) -> Optional[Dict[str, Any]]:
        """检查缓存"""
        try:
            cache_key = f"qa_cache:{hash(question) % 10000}"
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"缓存检查失败: {str(e)}")
        
        return None
    
    def _cache_result(self, question: str, result: Dict[str, Any]):
        """缓存结果"""
        try:
            cache_key = f"qa_cache:{hash(question) % 10000}"
            self.redis.setex(
                cache_key,
                86400,  # 24小时
                json.dumps(result, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"缓存保存失败: {str(e)}")
    
    async def _call_rag(self, question: str, question_type: str) -> Dict[str, Any]:
        """调用 RAG 服务检索知识库"""
        logger.info(f"📚 调用 RAG 服务查询: {question}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 根据问题类型确定搜索分类
                category_map = {
                    "sales_inquiry": "sales",
                    "hr_inquiry": "hr",
                    "technical_inquiry": "technical",
                    "financial_inquiry": "finance",
                    "customer_inquiry": "case_study"
                }
                category = category_map.get(question_type)
                
                search_payload = {
                    "query": question,
                    "top_k": 3,
                    "category": category,
                    "threshold": 0.5
                }
                
                async with session.post(
                    "http://rag_service:8000/api/rag/search",
                    json=search_payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"⚠️ RAG 服务返回错误: {resp.status}")
                        return {
                            "sources": [],
                            "content": "",
                            "confidence": 0.0,
                            "retrieval_status": "failed"
                        }
                    
                    data = await resp.json()
                    documents = data.get("documents", [])
                    
                    if not documents:
                        logger.info(f"❌ 知识库中未找到相关文档")
                        return {
                            "sources": [],
                            "content": "",
                            "confidence": 0.0,
                            "retrieval_status": "no_results",
                            "search_hint": "尝试使用不同的关键词或查看FAQ部分"
                        }
                    
                    # 提取文档内容
                    contents = [doc.get("content", "") for doc in documents if isinstance(doc, dict)]
                    sources = [doc.get("source", "") for doc in documents if isinstance(doc, dict)]
                    
                    combined_content = "\n".join(contents[:2])  # 最多取2个文档
                    
                    logger.info(f"✅ 知识库检索成功，找到 {len(documents)} 个相关文档")
                    
                    return {
                        "sources": sources,
                        "content": combined_content,
                        "confidence": 0.85,
                        "retrieval_status": "success",
                        "documents_count": len(documents)
                    }
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ RAG 服务超时")
            return {
                "sources": [],
                "content": "",
                "confidence": 0.0,
                "retrieval_status": "timeout"
            }
        except Exception as e:
            logger.error(f"🔴 调用 RAG 服务出错: {str(e)}")
            return {
                "sources": [],
                "content": "",
                "confidence": 0.0,
                "retrieval_status": "error",
                "error_message": str(e)
            }
    
    async def _call_agent(self, question: str, question_type: str, context: ContextData) -> Dict[str, Any]:
        """调用Agent服务（模拟）"""
        logger.info(f"调用Agent服务执行: {question}")
        
        # 模拟Agent调用企业系统
        if "sales" in question_type:
            return {
                "sources": ["erp_system"],
                "content": "Q1销售数据: 5000万元，同比增长15%",
                "confidence": 0.95
            }
        elif "hr" in question_type:
            return {
                "sources": ["hr_system"],
                "content": "当前员工总数: 500人，本月入职: 10人",
                "confidence": 0.90
            }
        else:
            return {
                "sources": [],
                "content": "",
                "confidence": 0.0
            }
    
    async def _generate_answer(
        self,
        question: str,
        rag_results: Dict[str, Any],
        agent_results: Dict[str, Any],
        context: ContextData
    ) -> str:
        """生成答案 - 调用真实LLM"""
        logger.info("调用真实LLM生成答案...")
        
        # 检查知识库检索结果
        has_knowledge = bool(rag_results.get("content"))
        has_agent_data = bool(agent_results.get("content"))
        
        # 组装上下文信息
        context_parts = []
        sources = []
        
        if agent_results.get("content"):
            context_parts.append(f"企业数据: {agent_results['content']}")
            sources.extend(agent_results.get("sources", []))
        
        if rag_results.get("content"):
            context_parts.append(f"知识库内容: {rag_results['content']}")
            sources.extend(rag_results.get("sources", []))
        
        # 标记检索过程
        retrieval_status = rag_results.get("retrieval_status", "unknown")
        
        # 构造调用 LLM 的 prompt
        if has_knowledge or has_agent_data:
            system_prompt = f"""你是一个企业AI助手。
请基于以下信息回答用户的问题：

{chr(10).join(context_parts)}

数据来源: {', '.join(sources)}

请提供清晰、准确的答案。"""
        else:
            # 即使没有找到知识库信息，也让 LLM 尝试回答
            system_prompt = """你是一个企业AI助手。
用户提出了一个问题，但知识库中没有找到相关信息。
请根据你的知识基础提供一个有帮助的答案。
如果需要，可以建议用户联系相关部门以获得更准确的信息。"""

        user_prompt = question
        
        try:
            # 调用真实 LLM API
            answer = await self._call_real_llm(system_prompt, user_prompt)
            logger.info(f"✅ LLM 生成答案成功，长度: {len(answer)}")
            
            # 如果没有知识库结果，添加说明
            if not has_knowledge and not has_agent_data:
                answer = f"📝 基于通用知识库的回答（知识库中未找到相关信息）：\n\n{answer}"
            
            return answer
        except Exception as e:
            logger.error(f"🔴 LLM 调用失败: {str(e)}，使用备选答案")
            # 如果 LLM 调用失败，返回带提示的简单答案
            if has_knowledge or has_agent_data:
                simple_answer = "根据我们掌握的信息：\n"
                if agent_results.get("content"):
                    simple_answer += f"\n企业数据反馈: {agent_results['content']}"
                if rag_results.get("content"):
                    simple_answer += f"\n知识库信息: {rag_results['content']}"
                simple_answer += f"\n\n📊 数据来源: {', '.join(sources)}"
                return simple_answer
            else:
                return "抱歉，我无法找到相关信息。请尝试用其他关键词提问，或联系管理员。"
    
    async def _call_real_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用真实 LLM 服务
        
        从 LLM Service 读取当前配置（provider 和 API Key）
        支持 OpenAI 和 ChatAnywhere
        """
        try:
            # 1. 创建新的 session 用于 LLM 调用
            async with aiohttp.ClientSession() as session:
                # 1a. 从 LLM Service 获取当前配置
                async with session.get(
                    "http://llm_service:8000/api/llm/config",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"获取 LLM 配置失败 ({resp.status}): {error_text}")
                    
                    config = await resp.json()
                    provider = config.get("provider", "openai")
                    model = config.get("model", "gpt-3.5-turbo")
                    status = config.get("status", "")
                    
                    if status == "not_configured":
                        raise Exception(f"LLM 提供商 {provider} 未配置 API Key")
                    
                    logger.info(f"🤖 使用已启用的 LLM: {provider.upper()}, 模型: {model}")
                
                # 2. 调用 LLM 服务的 chat 接口（LLM Service 会根据配置使用正确的提供商）
                payload = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "model": model,
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
                
                async with session.post(
                    "http://llm_service:8000/api/llm/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"LLM 服务返回错误 ({resp.status}): {error_text}")
                    
                    result = await resp.json()
                    answer = result.get("content") or ""
                    
                    if not answer:
                        raise Exception("LLM 返回空的答案")
                    
                    tokens = result.get("tokens_used", 0)
                    logger.info(f"✅ {provider.upper()} 返回答案，消耗 tokens: {tokens}")
                    return answer
        
        except asyncio.TimeoutError:
            logger.error("⏱️ LLM 服务请求超时（30秒）")
            raise Exception("LLM 服务请求超时")
        except Exception as e:
            logger.error(f"❌ 调用 LLM 出错: {str(e)}")
            raise
    
    async def _call_openai_llm(self, system_prompt: str, user_prompt: str, model_info: Dict[str, Any]) -> str:
        """
        调用 OpenAI API
        
        支持 GPT-4, GPT-3.5-turbo 等模型
        """
        try:
            import openai
            
            api_key = model_info.get("api_key")
            if not api_key or api_key == "sk-":
                raise Exception("OpenAI API Key 未配置")
            
            # 设置 API key
            openai.api_key = api_key
            
            # 确定要使用的模型名称
            model_name = model_info.get("name", "gpt-3.5-turbo").lower()
            if "gpt-4" in model_name:
                model = "gpt-4"
            else:
                model = "gpt-3.5-turbo"
            
            logger.info(f"📤 调用 OpenAI API，模型: {model}")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=model_info.get("temperature", 0.7),
                max_tokens=min(model_info.get("max_tokens", 2048), 4096),
                timeout=30
            )
            
            answer = response['choices'][0]['message']['content']
            tokens = response['usage']['total_tokens']
            logger.info(f"📥 OpenAI 返回: tokens={tokens}")
            
            return answer
            
        except Exception as e:
            logger.error(f"❌ OpenAI API 调用失败: {str(e)}")
            raise
    
    async def _call_chatanywhere_llm(self, system_prompt: str, user_prompt: str, model_info: Dict[str, Any]) -> str:
        """
        调用 ChatAnywhere API
        
        ChatAnywhere 提供免费的 ChatGPT API，兼容 OpenAI 接口
        GitHub: https://github.com/chatanywhere/ChatGPT_API_free
        
        API 端点: https://api.chatanywhere.com.cn/v1/chat/completions
        认证方式: Bearer Token (API Key)
        
        配置示例:
        - api_key: your-chatanywhere-api-key (从 https://chatanywhere.com.cn/ 获取)
        - name: ChatGPT / GPT-4 / Claude 等
        - temperature: 0.7
        - max_tokens: 2048
        """
        try:
            import openai
            
            api_key = model_info.get("api_key")
            if not api_key:
                raise Exception("ChatAnywhere API Key 未配置，请访问 https://chatanywhere.com.cn/ 获取")
            
            # ChatAnywhere 兼容 OpenAI 接口，需要配置自定义端点
            openai.api_key = api_key
            openai.api_base = "https://api.chatanywhere.com.cn/v1"
            
            # 获取模型名称，支持 gpt-3.5-turbo, gpt-4, claude 等
            model_name = model_info.get("name", "gpt-3.5-turbo").lower()
            
            # ChatAnywhere 支持的模型列表
            supported_models = {
                "gpt-4": "gpt-4",
                "gpt-3.5-turbo": "gpt-3.5-turbo",
                "gpt-3.5": "gpt-3.5-turbo",
                "chatgpt": "gpt-3.5-turbo",
                "claude": "claude-3-opus",  # 如果支持 Claude
            }
            
            # 匹配模型名称
            model = "gpt-3.5-turbo"  # 默认模型
            for key, value in supported_models.items():
                if key in model_name:
                    model = value
                    break
            
            logger.info(f"📤 调用 ChatAnywhere API，模型: {model}")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=model_info.get("temperature", 0.7),
                max_tokens=min(model_info.get("max_tokens", 2048), 4096),
                timeout=30
            )
            
            answer = response['choices'][0]['message']['content']
            tokens = response.get('usage', {}).get('total_tokens', 0)
            logger.info(f"📥 ChatAnywhere 返回: tokens={tokens}")
            
            return answer
            
        except Exception as e:
            logger.error(f"❌ ChatAnywhere API 调用失败: {str(e)}")
            raise
