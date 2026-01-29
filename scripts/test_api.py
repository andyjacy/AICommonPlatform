#!/usr/bin/env python3
"""
AI Common Platform - 测试脚本
用于测试各个服务的API
"""

import requests
import json
from typing import Dict, Any
import time

# 服务URL
SERVICES = {
    "qa_entry": "http://localhost:8001",
    "prompt_service": "http://localhost:8002",
    "rag_service": "http://localhost:8003",
    "agent_service": "http://localhost:8004",
    "integration": "http://localhost:8005",
    "llm_service": "http://localhost:8006",
}

class APITester:
    """API测试工具"""
    
    def __init__(self):
        self.results = []
    
    def test_health(self):
        """测试所有服务的健康检查"""
        print("\n" + "="*60)
        print("测试: 健康检查")
        print("="*60)
        
        for service_name, url in SERVICES.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name}: 健康")
                    self.results.append((service_name, "health", "PASS"))
                else:
                    print(f"❌ {service_name}: 异常 (状态码: {response.status_code})")
                    self.results.append((service_name, "health", "FAIL"))
            except Exception as e:
                print(f"❌ {service_name}: 连接失败 - {str(e)}")
                self.results.append((service_name, "health", "ERROR"))
    
    def test_qa_service(self):
        """测试问答服务"""
        print("\n" + "="*60)
        print("测试: 问答服务")
        print("="*60)
        
        # 测试1: 销售问题
        print("\n测试1: 销售问题")
        payload = {
            "question": "今年Q1的销售额是多少?",
            "user_id": "user123",
            "context": {"department": "sales"}
        }
        
        try:
            response = requests.post(
                f"{SERVICES['qa_entry']}/api/qa/ask",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 问题处理成功")
                print(f"   答案: {result.get('answer', '')[:100]}...")
                print(f"   置信度: {result.get('confidence', 0)}")
                print(f"   执行时间: {result.get('execution_time', 0):.2f}秒")
                self.results.append(("qa_entry", "sales_question", "PASS"))
            else:
                print(f"❌ 处理失败 (状态码: {response.status_code})")
                self.results.append(("qa_entry", "sales_question", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("qa_entry", "sales_question", "ERROR"))
        
        # 测试2: HR问题
        print("\n测试2: HR问题")
        payload = {
            "question": "公司有多少员工?",
            "user_id": "user456",
            "context": {"department": "hr"}
        }
        
        try:
            response = requests.post(
                f"{SERVICES['qa_entry']}/api/qa/ask",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 问题处理成功")
                print(f"   答案: {result.get('answer', '')[:100]}...")
                self.results.append(("qa_entry", "hr_question", "PASS"))
            else:
                print(f"❌ 处理失败")
                self.results.append(("qa_entry", "hr_question", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("qa_entry", "hr_question", "ERROR"))
    
    def test_prompt_service(self):
        """测试Prompt服务"""
        print("\n" + "="*60)
        print("测试: Prompt服务")
        print("="*60)
        
        # 获取模板列表
        print("\n获取Prompt模板列表...")
        try:
            response = requests.get(
                f"{SERVICES['prompt_service']}/api/prompts",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取成功，共{data.get('total', 0)}个模板")
                for template in data.get('templates', [])[:2]:
                    print(f"   - {template['name']} ({template['id']})")
                self.results.append(("prompt_service", "list_templates", "PASS"))
            else:
                print(f"❌ 获取失败")
                self.results.append(("prompt_service", "list_templates", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("prompt_service", "list_templates", "ERROR"))
        
        # 组装Prompt
        print("\n组装Prompt...")
        payload = {
            "template_id": "sales_advisor",
            "variables": {
                "question": "今年Q1的销售额是多少?",
                "sales_data": "Q1销售额5000万元",
                "customer_info": "主要客户ABC公司"
            },
            "role": "Sales Advisor"
        }
        
        try:
            response = requests.post(
                f"{SERVICES['prompt_service']}/api/prompts/assemble",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prompt组装成功")
                print(f"   长度: {len(result.get('prompt', ''))}个字符")
                self.results.append(("prompt_service", "assemble_prompt", "PASS"))
            else:
                print(f"❌ 组装失败")
                self.results.append(("prompt_service", "assemble_prompt", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("prompt_service", "assemble_prompt", "ERROR"))
    
    def test_rag_service(self):
        """测试RAG服务"""
        print("\n" + "="*60)
        print("测试: RAG服务")
        print("="*60)
        
        # 搜索知识库
        print("\n搜索知识库...")
        payload = {
            "query": "销售",
            "top_k": 3
        }
        
        try:
            response = requests.post(
                f"{SERVICES['rag_service']}/api/rag/search",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 搜索成功，找到{result.get('total', 0)}个文档")
                for doc in result.get('documents', [])[:2]:
                    print(f"   - {doc['title']}")
                self.results.append(("rag_service", "search", "PASS"))
            else:
                print(f"❌ 搜索失败")
                self.results.append(("rag_service", "search", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("rag_service", "search", "ERROR"))
    
    def test_agent_service(self):
        """测试Agent服务"""
        print("\n" + "="*60)
        print("测试: Agent服务")
        print("="*60)
        
        # 获取工具列表
        print("\n获取Agent工具列表...")
        try:
            response = requests.get(
                f"{SERVICES['agent_service']}/api/agent/tools",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取成功，共{data.get('total', 0)}个工具")
                for tool in data.get('tools', [])[:2]:
                    print(f"   - {tool['name']} ({tool['id']})")
                self.results.append(("agent_service", "list_tools", "PASS"))
            else:
                print(f"❌ 获取失败")
                self.results.append(("agent_service", "list_tools", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("agent_service", "list_tools", "ERROR"))
        
        # 执行任务
        print("\n执行Agent任务...")
        payload = {
            "question": "查询Q1销售数据和员工信息",
            "tools": ["erp_sales", "hrm_employee"]
        }
        
        try:
            response = requests.post(
                f"{SERVICES['agent_service']}/api/agent/execute",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 任务执行成功")
                print(f"   状态: {result.get('status')}")
                print(f"   执行工具: {len(result.get('executed_tools', []))}个")
                self.results.append(("agent_service", "execute_task", "PASS"))
            else:
                print(f"❌ 执行失败")
                self.results.append(("agent_service", "execute_task", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("agent_service", "execute_task", "ERROR"))
    
    def test_integration_service(self):
        """测试集成服务"""
        print("\n" + "="*60)
        print("测试: 企业系统集成服务")
        print("="*60)
        
        # 获取系统列表
        print("\n获取集成系统列表...")
        try:
            response = requests.get(
                f"{SERVICES['integration']}/api/integration/systems",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取成功，共{len(data.get('systems', []))}个系统")
                for system in data.get('systems', []):
                    print(f"   - {system['name']}: {system['description']}")
                self.results.append(("integration", "list_systems", "PASS"))
            else:
                print(f"❌ 获取失败")
                self.results.append(("integration", "list_systems", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("integration", "list_systems", "ERROR"))
        
        # 查询ERP数据
        print("\n查询ERP销售数据...")
        try:
            response = requests.get(
                f"{SERVICES['integration']}/api/integration/erp/sales/2024/Q1",
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 查询成功")
                print(f"   Q1销售额: {result['data']['amount']}万元")
                self.results.append(("integration", "erp_query", "PASS"))
            else:
                print(f"❌ 查询失败")
                self.results.append(("integration", "erp_query", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("integration", "erp_query", "ERROR"))
    
    def test_llm_service(self):
        """测试LLM服务"""
        print("\n" + "="*60)
        print("测试: LLM服务")
        print("="*60)
        
        # 获取模型列表
        print("\n获取可用模型列表...")
        try:
            response = requests.get(
                f"{SERVICES['llm_service']}/api/llm/models",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取成功，共{data.get('total', 0)}个模型")
                for model in data.get('models', [])[:3]:
                    print(f"   - {model}")
                self.results.append(("llm_service", "list_models", "PASS"))
            else:
                print(f"❌ 获取失败")
                self.results.append(("llm_service", "list_models", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("llm_service", "list_models", "ERROR"))
        
        # 文本完成
        print("\n测试文本完成...")
        payload = {
            "prompt": "今年Q1的销售额",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(
                f"{SERVICES['llm_service']}/api/llm/complete",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 完成成功")
                print(f"   模型: {result.get('model')}")
                print(f"   使用tokens: {result.get('tokens_used')}")
                self.results.append(("llm_service", "completion", "PASS"))
            else:
                print(f"❌ 完成失败")
                self.results.append(("llm_service", "completion", "FAIL"))
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            self.results.append(("llm_service", "completion", "ERROR"))
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        pass_count = sum(1 for _, _, status in self.results if status == "PASS")
        fail_count = sum(1 for _, _, status in self.results if status == "FAIL")
        error_count = sum(1 for _, _, status in self.results if status == "ERROR")
        
        print(f"\n总计: {len(self.results)}项测试")
        print(f"✅ 通过: {pass_count}")
        print(f"❌ 失败: {fail_count}")
        print(f"⚠️  异常: {error_count}")
        
        if fail_count + error_count > 0:
            print("\n失败/异常的测试:")
            for service, test, status in self.results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  - {service}.{test}: {status}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI Common Platform - API测试")
    print("="*60)
    
    tester = APITester()
    
    try:
        # 执行测试
        tester.test_health()
        time.sleep(1)
        
        tester.test_qa_service()
        time.sleep(1)
        
        tester.test_prompt_service()
        time.sleep(1)
        
        tester.test_rag_service()
        time.sleep(1)
        
        tester.test_agent_service()
        time.sleep(1)
        
        tester.test_integration_service()
        time.sleep(1)
        
        tester.test_llm_service()
        
        # 打印总结
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试异常: {str(e)}")

if __name__ == "__main__":
    main()
