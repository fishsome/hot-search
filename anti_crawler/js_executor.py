#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JS执行器 - 反爬虫高级组件
使用 PyExecJS 执行 JavaScript 加密/解密
"""

import execjs
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class JSExecutor:
    """JavaScript执行器"""

    def __init__(self, runtime: str = "Node"):
        """
        初始化JS执行环境
        
        Args:
            runtime: JS运行环境（Node/V8/PyV8等）
        """
        try:
            self.ctx = execjs.get(runtime)
            logger.info(f"JS执行环境初始化成功: {runtime}")
        except Exception as e:
            logger.warning(f"JS执行环境初始化失败: {e}")
            self.ctx = None

    def execute(self, js_code: str, func_name: str = None, *args) -> Optional[Any]:
        """
        执行JS代码
        
        Args:
            js_code: JavaScript代码
            func_name: 要调用的函数名
            args: 函数参数
        
        Returns:
            执行结果
        """
        if not self.ctx:
            logger.error("JS执行环境未初始化")
            return None
        
        try:
            # 如果提供了函数名，调用该函数
            if func_name:
                # 先编译整个代码
                self.ctx.eval(js_code)
                # 然后调用函数
                result = self.ctx.call(func_name, *args)
            else:
                # 直接执行代码
                result = self.ctx.eval(js_code)
            
            return result
        except Exception as e:
            logger.error(f"JS执行失败: {e}")
            return None

    def decrypt_token(self, encrypted: str, js_code: str) -> Optional[str]:
        """
        解密网站token（常见反爬手段）
        
        Args:
            encrypted: 加密的字符串
            js_code: 解密JS代码
        
        Returns:
            解密后的token
        """
        return self.execute(js_code, "decrypt", encrypted)

    def generate_sign(self, params: Dict[str, Any], js_code: str) -> Optional[str]:
        """
        生成请求签名（常见反爬手段）
        
        Args:
            params: 请求参数
            js_code: 签名生成JS代码
        
        Returns:
            签名字符串
        """
        return self.execute(js_code, "generateSign", params)


# 预定义的JS加密函数库（常见网站的加密方式）
JS_LIB = {
    # 百度搜索加密（示例）
    "baidu_encrypt": """
    function encrypt(text) {
        // 百度加密逻辑（简化示例）
        var result = '';
        for (var i = 0; i < text.length; i++) {
            result += String.fromCharCode(text.charCodeAt(i) + 1);
        }
        return result;
    }
    """,
    
    # Sougou搜索加密（示例）
    "sougou_encrypt": """
    function encrypt(text) {
        // Sougou加密逻辑（简化示例）
        return encodeURIComponent(text);
    }
    """,
    
    # 通用MD5加密
    "md5": """
    function md5(string) {
        // MD5实现（简化，实际需要完整MD5库）
        // 这里只是示例，实际使用需要引入crypto-js等库
        return string; // placeholder
    }
    """,
}


if __name__ == "__main__":
    # 测试
    executor = JSExecutor()
    
    # 测试百度加密
    if executor.ctx:
        result = executor.execute(JS_LIB["baidu_encrypt"], "encrypt", "test")
        print(f"加密结果: {result}")