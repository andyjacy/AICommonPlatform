#!/usr/bin/env python3
"""
AI Platform Configuration and Verification Tool
This script helps you configure and verify the AI platform setup
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

class ConfigValidator:
    """Validates AI platform configuration"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
        self.config = {}
        
    def load_env(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        if not self.env_file.exists():
            print_error(f".env file not found at {self.env_file}")
            return {}
            
        config = {}
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            self.config = config
            return config
        except Exception as e:
            print_error(f"Failed to load .env file: {e}")
            return {}
    
    def check_env_file(self) -> bool:
        """Check if .env file exists and is readable"""
        print_info("Checking .env file...")
        
        if not self.env_file.exists():
            print_error(f".env file not found at {self.env_file}")
            print_info(f"Creating .env from .env.example...")
            
            if self.env_example.exists():
                with open(self.env_example, 'r') as src:
                    content = src.read()
                with open(self.env_file, 'w') as dst:
                    dst.write(content)
                print_success(".env file created from .env.example")
                return True
            else:
                print_error(".env.example not found either")
                return False
        
        print_success(".env file found")
        
        # Check permissions
        try:
            with open(self.env_file, 'r') as f:
                f.read(1)
            print_success(".env file is readable")
            return True
        except PermissionError:
            print_error(".env file is not readable (permission denied)")
            return False
    
    def check_api_key(self) -> Tuple[bool, str]:
        """Check if API key is configured"""
        print_info("Checking API Key...")
        
        self.load_env()
        api_key = self.config.get('OPENAI_API_KEY', '').strip()
        
        if not api_key:
            print_error("OPENAI_API_KEY is not set or empty")
            return False, ""
        
        if api_key == 'your-api-key-here':
            print_error("OPENAI_API_KEY is still set to default value")
            return False, api_key
        
        if not api_key.startswith('sk-'):
            print_warning("OPENAI_API_KEY doesn't start with 'sk-' (might be invalid)")
            return False, api_key
        
        # Don't print the full key
        masked_key = api_key[:10] + '...' + api_key[-5:]
        print_success(f"OPENAI_API_KEY is configured ({masked_key})")
        return True, api_key
    
    def check_gitignore(self) -> bool:
        """Check if .gitignore includes .env"""
        print_info("Checking .gitignore...")
        
        gitignore = self.project_root / '.gitignore'
        if not gitignore.exists():
            print_warning(".gitignore file not found")
            return False
        
        with open(gitignore, 'r') as f:
            content = f.read()
        
        if '.env' in content:
            print_success(".gitignore includes .env")
            return True
        else:
            print_error(".gitignore does not include .env")
            print_info("Adding .env to .gitignore...")
            with open(gitignore, 'a') as f:
                f.write('\n.env\n.env.local\n.env.*.local\n')
            print_success(".env added to .gitignore")
            return True
    
    def check_docker(self) -> bool:
        """Check if Docker is installed and running"""
        print_info("Checking Docker...")
        
        try:
            result = subprocess.run(['docker', '--version'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Docker is installed: {result.stdout.strip()}")
                
                # Check if Docker daemon is running
                result = subprocess.run(['docker', 'info'], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    print_success("Docker daemon is running")
                    return True
                else:
                    print_error("Docker daemon is not running")
                    print_info("Try: open --background -a Docker")
                    return False
            else:
                print_error("Docker is not installed")
                print_info("Visit: https://www.docker.com/products/docker-desktop")
                return False
        except FileNotFoundError:
            print_error("Docker is not installed")
            return False
    
    def check_docker_compose(self) -> bool:
        """Check if Docker Compose is installed"""
        print_info("Checking Docker Compose...")
        
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Docker Compose is installed: {result.stdout.strip()}")
                return True
            else:
                print_error("Docker Compose is not installed")
                return False
        except FileNotFoundError:
            print_error("Docker Compose is not installed")
            print_info("Visit: https://docs.docker.com/compose/install/")
            return False
    
    def check_ports(self) -> bool:
        """Check if required ports are available"""
        print_info("Checking ports...")
        
        ports = {
            3000: 'Web UI',
            8001: 'LLM Service',
            8002: 'Prompt Service'
        }
        
        all_free = True
        for port, service in ports.items():
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print_error(f"Port {port} ({service}) is already in use")
                    all_free = False
                else:
                    print_success(f"Port {port} ({service}) is available")
            except FileNotFoundError:
                print_warning("lsof command not found, skipping port check")
                return True
        
        return all_free
    
    def check_services(self) -> bool:
        """Check if services are running"""
        print_info("Checking services...")
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', 'docker-compose.lite.yml', 'ps'],
                cwd=self.project_root,
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print_warning("Could not get service status")
                return False
            
            output = result.stdout
            if 'Up' in output:
                print_success("Services are running")
                return True
            else:
                print_warning("Some services are not running")
                return False
                
        except Exception as e:
            print_warning(f"Could not check services: {e}")
            return False

def test_api_endpoints(base_url: str = "http://localhost:8002") -> bool:
    """Test API endpoints"""
    print_info("Testing API endpoints...")
    
    endpoints = [
        ('/api/prompts', 'GET', 'Prompt templates'),
        ('/api/agent/tools', 'GET', 'Agent tools'),
        ('/docs', 'GET', 'API documentation'),
    ]
    
    all_ok = True
    for path, method, description in endpoints:
        try:
            if method == 'GET':
                result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                     f'{base_url}{path}'],
                    capture_output=True, text=True, timeout=5
                )
                status = result.stdout
                
                if status.startswith('2'):
                    print_success(f"{method} {path} ({description}) - {status}")
                elif status.startswith('4'):
                    print_warning(f"{method} {path} ({description}) - {status}")
                else:
                    print_error(f"{method} {path} ({description}) - {status}")
                    all_ok = False
            
        except subprocess.TimeoutExpired:
            print_error(f"{method} {path} ({description}) - timeout")
            all_ok = False
        except Exception as e:
            print_error(f"{method} {path} ({description}) - {e}")
            all_ok = False
    
    return all_ok

def setup_env_interactive() -> bool:
    """Interactive setup of .env file"""
    print_header("🔧 Interactive Setup")
    
    env_file = Path('.env')
    
    print(f"{Colors.BOLD}Fill in your configuration below:{Colors.ENDC}\n")
    
    # OpenAI API Key
    print(f"{Colors.BOLD}OpenAI Configuration (Required):{Colors.ENDC}")
    api_key = input(f"Enter your OpenAI API Key (sk-...): ").strip()
    model = input(f"Select model (gpt-4/gpt-3.5-turbo) [gpt-4]: ").strip() or "gpt-4"
    
    # Alternative LLMs
    print(f"\n{Colors.BOLD}Alternative LLM Configurations (Optional):{Colors.ENDC}")
    alibaba_key = input(f"Enter Alibaba API Key (or press Enter to skip): ").strip()
    baidu_key = input(f"Enter Baidu API Key (or press Enter to skip): ").strip()
    
    # Enterprise Systems
    print(f"\n{Colors.BOLD}Enterprise Systems (Optional):{Colors.ENDC}")
    erp_url = input(f"Enter ERP API URL (or press Enter to skip): ").strip()
    crm_url = input(f"Enter CRM API URL (or press Enter to skip): ").strip()
    
    # System Settings
    print(f"\n{Colors.BOLD}System Settings:{Colors.ENDC}")
    log_level = input(f"Select log level (INFO/DEBUG) [INFO]: ").strip() or "INFO"
    use_mock = input(f"Use mock data for development? (y/n) [n]: ").strip().lower()
    
    # Generate .env content
    env_content = f"""# AI Platform Configuration

# ==================== OpenAI Configuration ====================
OPENAI_API_KEY={api_key}
OPENAI_MODEL={model}

# ==================== Alternative LLM Configuration ====================
ALIBABA_API_KEY={alibaba_key or 'your-key-here'}
ALIBABA_MODEL=qwen-plus

BAIDU_API_KEY={baidu_key or 'your-key-here'}
BAIDU_SECRET_KEY=
BAIDU_MODEL=ernie-4.0

XUNFEI_API_KEY=
XUNFEI_APP_ID=
XUNFEI_MODEL=sparkdesk-v3.1

ZHIPU_API_KEY=
ZHIPU_MODEL=glm-4

# ==================== Enterprise System Integration ====================
ERP_API_URL={erp_url or 'http://erp-system:8000'}
ERP_API_KEY=

CRM_API_URL={crm_url or 'http://crm-system:8000'}
CRM_API_KEY=

HRM_API_URL=http://hrm-system:8000
HRM_API_KEY=

# ==================== System Configuration ====================
LOG_LEVEL={log_level}
CACHE_TTL=3600
USE_MOCK_DATA={'true' if use_mock == 'y' else 'false'}
DEBUG=false
"""
    
    # Save .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        # Secure permissions (Unix-like systems)
        os.chmod(env_file, 0o600)
        
        print_success(f"\n✓ .env file created and saved")
        print_info(f"Location: {env_file.absolute()}")
        print_warning(f"File permissions set to 600 (owner only)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def main():
    """Main entry point"""
    print_header("🤖 AI Platform Setup & Verification Tool")
    
    validator = ConfigValidator()
    
    # Phase 1: Check prerequisites
    print(f"{Colors.BOLD}Phase 1: Checking Prerequisites{Colors.ENDC}\n")
    
    checks = [
        ("Docker", validator.check_docker()),
        ("Docker Compose", validator.check_docker_compose()),
        (".env file", validator.check_env_file()),
        ("API Key", validator.check_api_key()[0]),
        (".gitignore", validator.check_gitignore()),
        ("Available ports", validator.check_ports()),
    ]
    
    all_passed = all(result for _, result in checks)
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    for check_name, passed in checks:
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"  {status} {check_name}")
    
    if not all_passed:
        print_warning("\n⚠ Some checks failed. Please address the issues above.")
        
        if not validator.check_env_file():
            setup = input(f"\nWould you like to setup .env interactively? (y/n): ").lower()
            if setup == 'y':
                setup_env_interactive()
        
        return 1
    
    # Phase 2: Start containers
    print(f"\n{Colors.BOLD}Phase 2: Docker Services{Colors.ENDC}\n")
    
    print_info("Starting Docker containers...")
    
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.lite.yml', 'up', '-d', '--build'],
            cwd=validator.project_root,
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print_success("Docker containers started successfully")
            
            print_info("Waiting for services to be ready (10 seconds)...")
            time.sleep(10)
            
            # Phase 3: Test endpoints
            print(f"\n{Colors.BOLD}Phase 3: Testing API Endpoints{Colors.ENDC}\n")
            test_ok = test_api_endpoints()
            
            if test_ok:
                print_success("\nAll API endpoints are responding correctly!")
            else:
                print_warning("\nSome API endpoints are not responding yet.")
                print_info("Services might still be starting up. Check logs with:")
                print_info("docker-compose -f docker-compose.lite.yml logs")
        else:
            print_error(f"Failed to start containers: {result.stderr}")
            return 1
            
    except Exception as e:
        print_error(f"Error starting containers: {e}")
        return 1
    
    # Final summary
    print_header("✅ Setup Complete!")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")
    print(f"1. {Colors.OKCYAN}Web UI:{Colors.ENDC}")
    print(f"   → http://localhost:3000")
    print(f"\n2. {Colors.OKCYAN}Admin Console:{Colors.ENDC}")
    print(f"   → http://localhost:3000/admin")
    print(f"\n3. {Colors.OKCYAN}API Documentation:{Colors.ENDC}")
    print(f"   → http://localhost:8002/docs")
    print(f"\n4. {Colors.OKCYAN}View Logs:{Colors.ENDC}")
    print(f"   → docker-compose -f docker-compose.lite.yml logs -f")
    print(f"\n5. {Colors.OKCYAN}Stop Services:{Colors.ENDC}")
    print(f"   → docker-compose -f docker-compose.lite.yml down")
    
    print(f"\n{Colors.BOLD}Documentation:{Colors.ENDC}")
    print(f"→ QUICK_REFERENCE.md (5 min quick start)")
    print(f"→ DEPLOYMENT_GUIDE.md (complete setup guide)")
    print(f"→ SECURITY_GUIDE.md (security best practices)")
    
    print_success("\n🎉 AI Platform is ready to use!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
