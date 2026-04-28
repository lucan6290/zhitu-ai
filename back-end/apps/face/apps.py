import os
import sys
import subprocess
import time
from pathlib import Path
from django.apps import AppConfig
from django.conf import settings


class FaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.face'
    verbose_name = '人脸识别管理'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        if os.environ.get('MCP_SERVER_STARTED') == 'true':
            return
        
        self._start_mcp_server()

    def _start_mcp_server(self):
        """启动 MCP Server 作为子进程"""
        try:
            base_dir = Path(__file__).resolve().parent.parent.parent
            mcp_server_path = base_dir / 'ai' / 'mcp' / 'server.py'
            
            env = os.environ.copy()
            env.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            env['MCP_SERVER_STARTED'] = 'true'
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            subprocess.Popen(
                [sys.executable, str(mcp_server_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                creationflags=creationflags
            )
            
            time.sleep(1)
            mcp_url = getattr(settings, 'MCP_SERVER_URL', 'http://127.0.0.1:8081/mcp')
            print(f"[MCP Server] 已自动启动: {mcp_url}")
            
        except Exception as e:
            print(f"[MCP Server] 启动失败: {e}")
