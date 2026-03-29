#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 工具模块
"""

from .config import get_config, get_config_manager, Config, ConfigManager
from .anti_crawl import (
    get_random_ua,
    get_headers,
    get_random_referer,
    retry_request,
    create_retry_session,
    safe_request,
    CookieManager,
    RateLimit,
)
from .dedup import deduplicate_by_title, cluster_by_topic, similarity, normalize_title
from .output import to_markdown, to_json, to_table, to_simple_list

__all__ = [
    # config
    "get_config",
    "get_config_manager",
    "Config",
    "ConfigManager",
    # anti_crawl
    "get_random_ua",
    "get_headers",
    "get_random_referer",
    "retry_request",
    "create_retry_session",
    "safe_request",
    "CookieManager",
    "RateLimit",
    # dedup
    "deduplicate_by_title",
    "cluster_by_topic",
    "similarity",
    "normalize_title",
    # output
    "to_markdown",
    "to_json",
    "to_table",
    "to_simple_list",
]