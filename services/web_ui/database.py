"""
SQLite 数据库管理模块
支持 LLM 模型配置、Prompt 模板、Agent 工具的持久化存储
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

DB_PATH = os.getenv("DB_PATH", "web_ui.db")

# 线程本地存储，确保每个线程有独立的数据库连接
_thread_local = threading.local()

def get_db_connection():
    """获取数据库连接（线程安全）"""
    if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
        _thread_local.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _thread_local.connection.row_factory = sqlite3.Row
        # 启用外键约束
        _thread_local.connection.execute("PRAGMA foreign_keys = ON")
    return _thread_local.connection

def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # LLM 模型表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            provider TEXT NOT NULL,
            model_type TEXT DEFAULT 'api',  -- 'api' 或 'local'
            endpoint TEXT,
            api_key TEXT,
            base_url TEXT,
            max_tokens INTEGER DEFAULT 2048,
            temperature REAL DEFAULT 0.7,
            top_p REAL DEFAULT 1.0,
            enabled BOOLEAN DEFAULT 1,
            is_default BOOLEAN DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT  -- JSON 格式的额外信息
        )
    """)
    
    # Prompt 模板表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            system_prompt TEXT NOT NULL,
            variables TEXT,  -- JSON 数组
            version TEXT DEFAULT '1.0',
            enabled BOOLEAN DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT  -- JSON 格式的额外信息
        )
    """)
    
    # Agent 工具表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            tool_type TEXT NOT NULL,  -- 'api', 'function', 'webhook'
            endpoint TEXT,
            method TEXT DEFAULT 'GET',  -- GET, POST, PUT, DELETE
            parameters TEXT,  -- JSON 格式
            enabled BOOLEAN DEFAULT 1,
            version TEXT DEFAULT '1.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT  -- JSON 格式的额外信息
        )
    """)
    
    # 配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

# ==================== LLM 模型管理 ====================

def add_llm_model(
    name: str,
    provider: str,
    model_type: str = "api",
    endpoint: str = None,
    api_key: str = None,
    base_url: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    top_p: float = 1.0,
    description: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """添加 LLM 模型"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO llm_models 
            (name, provider, model_type, endpoint, api_key, base_url, max_tokens, temperature, top_p, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, provider, model_type, endpoint, api_key, base_url,
            max_tokens, temperature, top_p, description, json.dumps(metadata or {})
        ))
        conn.commit()
        model_id = cursor.lastrowid
        return {"id": model_id, "name": name, "status": "success"}
    except sqlite3.IntegrityError:
        return {"error": f"模型 {name} 已存在"}
    except Exception as e:
        return {"error": str(e)}

def get_llm_models(enabled_only: bool = False) -> List[Dict[str, Any]]:
    """获取 LLM 模型列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM llm_models"
    if enabled_only:
        query += " WHERE enabled = 1"
    query += " ORDER BY is_default DESC, created_at"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    models = []
    for row in rows:
        model = dict(row)
        if model.get('metadata'):
            model['metadata'] = json.loads(model['metadata'])
        if model.get('variables'):
            model['variables'] = json.loads(model['variables'])
        models.append(model)
    
    return models

def get_llm_model(model_id: int = None, name: str = None) -> Optional[Dict[str, Any]]:
    """获取单个 LLM 模型"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if model_id:
        cursor.execute("SELECT * FROM llm_models WHERE id = ?", (model_id,))
    elif name:
        cursor.execute("SELECT * FROM llm_models WHERE name = ?", (name,))
    else:
        return None
    
    row = cursor.fetchone()
    if row:
        model = dict(row)
        if model.get('metadata'):
            model['metadata'] = json.loads(model['metadata'])
        return model
    return None

def update_llm_model(model_id: int, **kwargs) -> Dict[str, Any]:
    """更新 LLM 模型"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 只允许更新的字段
    allowed_fields = {
        'name', 'provider', 'endpoint', 'api_key', 'base_url',
        'max_tokens', 'temperature', 'top_p', 'enabled', 'is_default',
        'description', 'metadata'
    }
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not updates:
        return {"error": "没有可更新的字段"}
    
    updates['updated_at'] = datetime.now().isoformat()
    
    # 处理 metadata
    if 'metadata' in updates and isinstance(updates['metadata'], dict):
        updates['metadata'] = json.dumps(updates['metadata'])
    
    # 如果设置为默认，其他模型要取消默认
    if updates.get('is_default'):
        cursor.execute("UPDATE llm_models SET is_default = 0")
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [model_id]
    
    try:
        cursor.execute(f"UPDATE llm_models SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return {"id": model_id, "status": "updated"}
    except Exception as e:
        return {"error": str(e)}

def delete_llm_model(model_id: int) -> Dict[str, Any]:
    """删除 LLM 模型"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM llm_models WHERE id = ?", (model_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"status": "deleted"}
        else:
            return {"error": "模型不存在"}
    except Exception as e:
        return {"error": str(e)}

def get_default_llm_model() -> Optional[Dict[str, Any]]:
    """获取默认 LLM 模型"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM llm_models WHERE is_default = 1 AND enabled = 1")
    row = cursor.fetchone()
    
    if row:
        model = dict(row)
        if model.get('metadata'):
            model['metadata'] = json.loads(model['metadata'])
        return model
    return None

# ==================== Prompt 模板管理 ====================

def add_prompt(
    name: str,
    role: str,
    system_prompt: str,
    variables: List[str] = None,
    description: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """添加 Prompt 模板"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO prompts 
            (name, role, system_prompt, variables, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name, role, system_prompt,
            json.dumps(variables or []), description,
            json.dumps(metadata or {})
        ))
        conn.commit()
        prompt_id = cursor.lastrowid
        return {"id": prompt_id, "name": name, "status": "success"}
    except sqlite3.IntegrityError:
        return {"error": f"Prompt {name} 已存在"}
    except Exception as e:
        return {"error": str(e)}

def get_prompts(enabled_only: bool = False) -> List[Dict[str, Any]]:
    """获取 Prompt 模板列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM prompts"
    if enabled_only:
        query += " WHERE enabled = 1"
    query += " ORDER BY created_at"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    prompts = []
    for row in rows:
        prompt = dict(row)
        if prompt.get('variables'):
            prompt['variables'] = json.loads(prompt['variables'])
        if prompt.get('metadata'):
            prompt['metadata'] = json.loads(prompt['metadata'])
        prompts.append(prompt)
    
    return prompts

# ==================== Agent 工具管理 ====================

def add_agent_tool(
    name: str,
    description: str,
    tool_type: str,
    endpoint: str = None,
    method: str = "GET",
    parameters: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """添加 Agent 工具"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO agent_tools 
            (name, description, tool_type, endpoint, method, parameters, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, description, tool_type, endpoint, method,
            json.dumps(parameters or {}),
            json.dumps(metadata or {})
        ))
        conn.commit()
        tool_id = cursor.lastrowid
        return {"id": tool_id, "name": name, "status": "success"}
    except sqlite3.IntegrityError:
        return {"error": f"工具 {name} 已存在"}
    except Exception as e:
        return {"error": str(e)}

def get_agent_tools(enabled_only: bool = False) -> List[Dict[str, Any]]:
    """获取 Agent 工具列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM agent_tools"
    if enabled_only:
        query += " WHERE enabled = 1"
    query += " ORDER BY created_at"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    tools = []
    for row in rows:
        tool = dict(row)
        if tool.get('parameters'):
            tool['parameters'] = json.loads(tool['parameters'])
        if tool.get('metadata'):
            tool['metadata'] = json.loads(tool['metadata'])
        tools.append(tool)
    
    return tools

# ==================== 配置管理 ====================

def set_config(key: str, value: str, description: str = None) -> Dict[str, Any]:
    """设置配置项"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 尝试更新
        cursor.execute("UPDATE config SET value = ?, description = ?, updated_at = ? WHERE key = ?",
                      (value, description, datetime.now().isoformat(), key))
        
        # 如果没有更新行，则插入
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO config (key, value, description) VALUES (?, ?, ?)",
                          (key, value, description))
        
        conn.commit()
        return {"key": key, "status": "saved"}
    except Exception as e:
        return {"error": str(e)}

def get_config(key: str) -> Optional[str]:
    """获取配置项"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = cursor.fetchone()
    
    return row[0] if row else None

def get_all_configs() -> Dict[str, str]:
    """获取所有配置"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM config")
    rows = cursor.fetchall()
    
    return {row[0]: row[1] for row in rows}

# ==================== 数据库导出/导入 ====================

def export_data() -> Dict[str, Any]:
    """导出所有数据"""
    return {
        "llm_models": get_llm_models(),
        "prompts": get_prompts(),
        "agent_tools": get_agent_tools(),
        "config": get_all_configs(),
        "exported_at": datetime.now().isoformat()
    }

def import_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """导入数据"""
    result = {
        "llm_models": 0,
        "prompts": 0,
        "agent_tools": 0,
        "config": 0,
        "errors": []
    }
    
    # 导入 LLM 模型
    for model in data.get('llm_models', []):
        res = add_llm_model(**{k: v for k, v in model.items() if k != 'id'})
        if 'id' in res:
            result['llm_models'] += 1
        else:
            result['errors'].append(f"LLM Model: {res.get('error')}")
    
    # 导入 Prompts
    for prompt in data.get('prompts', []):
        res = add_prompt(**{k: v for k, v in prompt.items() if k != 'id'})
        if 'id' in res:
            result['prompts'] += 1
        else:
            result['errors'].append(f"Prompt: {res.get('error')}")
    
    # 导入 Agent 工具
    for tool in data.get('agent_tools', []):
        res = add_agent_tool(**{k: v for k, v in tool.items() if k != 'id'})
        if 'id' in res:
            result['agent_tools'] += 1
        else:
            result['errors'].append(f"Agent Tool: {res.get('error')}")
    
    # 导入配置
    for key, value in data.get('config', {}).items():
        set_config(key, str(value))
        result['config'] += 1
    
    return result
