from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import aiohttp
import uuid

app = FastAPI(
    title="AI Common Platform - LLM Service",
    description="大模型接口和管理服务 - 支持OpenAI和ChatAnywhere",
    version="2.0.0"
)

# ==================== 模型 ====================
class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000

class ChatResponse(BaseModel):
    """聊天响应"""
    id: str
    content: str
    model: str
    tokens_used: int
    stop_reason: str
    created_at: datetime

# ==================== 全局配置 ====================
llm_config = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_api_url": os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
    "chatanywhere_api_key": os.getenv("CHATANYWHERE_API_KEY", ""),
    "chatanywhere_api_url": os.getenv("CHATANYWHERE_API_URL", "https://api.chatanywhere.com.cn/v1"),
    "model_name": os.getenv("LLM_MODEL", "gpt-3.5-turbo")
}

async def call_openai_api(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> str:
    """调用 OpenAI API"""
    if not llm_config['openai_api_key']:
        raise HTTPException(status_code=400, detail="OpenAI API Key not configured")
    
    headers = {
        "Authorization": f"Bearer {llm_config['openai_api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{llm_config['openai_api_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=f"OpenAI API error: {error_text}")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to OpenAI: {str(e)}")

async def call_chatanywhere_api(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> str:
    """调用 ChatAnywhere API"""
    if not llm_config['chatanywhere_api_key']:
        raise HTTPException(status_code=400, detail="ChatAnywhere API Key not configured")
    
    headers = {
        "Authorization": f"Bearer {llm_config['chatanywhere_api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{llm_config['chatanywhere_api_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=f"ChatAnywhere API error: {error_text}")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to ChatAnywhere: {str(e)}")

# ==================== 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "llm_service",
        "provider": llm_config['provider'],
        "version": "2.0.0"
    }

@app.get("/api/llm/config")
async def get_config():
    """获取当前LLM配置"""
    provider = llm_config['provider']
    
    if provider == "openai":
        has_key = bool(llm_config['openai_api_key'])
        api_url = llm_config['openai_api_url']
    else:
        has_key = bool(llm_config['chatanywhere_api_key'])
        api_url = llm_config['chatanywhere_api_url']
    
    return {
        "provider": provider,
        "model": llm_config['model_name'],
        "api_url": api_url,
        "status": "configured" if has_key else "not_configured"
    }

@app.post("/api/llm/config")
async def update_config(
    provider: str = "openai",
    api_key: str = "",
    api_url: Optional[str] = None,
    model: str = "gpt-3.5-turbo"
):
    """更新LLM配置"""
    if provider not in ["openai", "chatanywhere"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    llm_config['provider'] = provider
    llm_config['model_name'] = model
    
    if provider == "openai":
        llm_config['openai_api_key'] = api_key
        if api_url:
            llm_config['openai_api_url'] = api_url
    else:
        llm_config['chatanywhere_api_key'] = api_key
        if api_url:
            llm_config['chatanywhere_api_url'] = api_url
    
    return {
        "status": "success",
        "message": f"LLM configured to use {provider}",
        "provider": provider,
        "model": model
    }

@app.post("/api/llm/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """聊天完成端点"""
    provider = llm_config['provider']
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    try:
        if provider == "openai":
            response_text = await call_openai_api(messages, request.model, request.temperature, request.max_tokens)
        elif provider == "chatanywhere":
            response_text = await call_chatanywhere_api(messages, request.model, request.temperature, request.max_tokens)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        tokens_used = sum(len(msg['content'].split()) for msg in messages) + len(response_text.split())
        
        return ChatResponse(
            id=f"chatcmpl_{uuid.uuid4().hex}",
            content=response_text,
            model=request.model,
            tokens_used=tokens_used,
            stop_reason="stop",
            created_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@app.get("/api/llm/models")
async def list_models():
    """获取支持的模型列表"""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "chatanywhere": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
    }
    
    return {
        "current_provider": llm_config['provider'],
        "supported_models": models,
        "default_model": llm_config['model_name']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
