import os
import time
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()


class APIConfig:
    def __init__(self):
        self.amadeus_api_key = "6VI59RCfSUaykDxeRa5GSO6arTqdAqGl"
        self.amadeus_api_secret = "gAiUpG7C6UJbsndp"
        self.serper_api_key = "20932e8b51564ab58eadd7aeb63c3d3bca814788"

        # 添加令牌管理属性
        self.access_token = None
        self.token_expiry = None

    def get_amadeus_token(self) -> str:
        """获取Amadeus API访问令牌 - 修复版"""
        # 如果令牌存在且未过期，直接返回
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            print(f"✅ 使用缓存令牌: {self.access_token[:10]}...")
            return self.access_token

        # 否则获取新令牌
        return self._get_new_access_token()

    def _get_new_access_token(self) -> Optional[str]:
        """获取新的Amadeus OAuth2访问令牌"""
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.amadeus_api_key,
            'client_secret': self.amadeus_api_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:

            print(f" use API Key: {self.amadeus_api_key[:10]}...")

            response = requests.post(token_url, data=data, headers=headers, timeout=10)

            print(f"📡 令牌请求状态码: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 1799)  # 默认1799秒（约30分钟）
                self.token_expiry = time.time() + expires_in - 60  # 提前60秒过期

                print(f" 令牌获取成功，有效期: {expires_in}秒")
                print(f" 新令牌: {self.access_token[:10]}...")
                return self.access_token
            else:
                print(f" 令牌获取失败: {response.status_code}")
                print(f" 错误响应: {response.text}")
                return None

        except Exception as e:
            print(f"🚨 获取令牌异常: {e}")
            return None

    def validate_config(self) -> bool:
        """验证API配置是否完整"""
        return all([
            self.amadeus_api_key,
            self.amadeus_api_secret,
            self.serper_api_key
        ])


