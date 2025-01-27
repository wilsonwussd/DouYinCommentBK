import httpx
import asyncio
import time
from datetime import datetime
from loguru import logger
from .models import db, Comment
import sys
import os
from typing import List, Dict
from flask import current_app

# 添加 DouyinComments 目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
douyin_comments_dir = os.path.join(project_root, 'DouyinComments')
sys.path.append(douyin_comments_dir)

# 导入 common 模块
from common import common

class CommentService:
    def __init__(self):
        self.base_url = "https://www.douyin.com/aweme/v1/web/comment/list/"
        self.cookie = self._get_cookie()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

    def _get_cookie(self) -> str:
        """从环境变量或文件加载cookie"""
        # 首先尝试从环境变量获取
        cookie = os.getenv("DOUYIN_COOKIE")
        if cookie:
            logger.info("从环境变量加载cookie成功")
            return cookie
            
        # 然后尝试从文件获取
        cookie_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookie.txt")
        if not os.path.exists(cookie_file):
            raise Exception("Cookie未加载，请先设置DOUYIN_COOKIE环境变量或创建cookie.txt文件")
            
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookie = f.read().strip()
            if not cookie:
                raise Exception("Cookie文件为空")
        
        logger.info("从文件加载cookie成功")
        return cookie
        
    async def fetch_comments(self, video_id: str, cursor: str = "0", count: str = "20"):
        """获取评论数据"""
        try:
            params = {
                "aweme_id": video_id,
                "cursor": cursor,
                "count": count,
                "item_type": "0"
            }
            
            headers = {
                "Cookie": self.cookie,
                "User-Agent": self.user_agent,
                "Referer": f"https://www.douyin.com/video/{video_id}",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            
            # 使用 common 函数处理参数和生成签名
            params, headers = common(self.base_url, params, headers)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(self.base_url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status_code") != 0:
                    raise ValueError(f"API返回错误: {data.get('status_msg', '未知错误')}")
                    
                return data.get("comments", []), data.get("has_more", False)
                
        except Exception as e:
            logger.error(f"获取评论失败: {str(e)}")
            raise

    async def collect_comments(self, video_id: str, max_comments: int = 100):
        """采集指定数量的评论"""
        collected_comments = []
        cursor = "0"
        retries = 3
        batch_size = min(20, max_comments)  # 控制每批次的大小
        
        try:
            while len(collected_comments) < max_comments and retries > 0:
                try:
                    comments, has_more = await self.fetch_comments(video_id, cursor, str(batch_size))
                    
                    if not comments:
                        break
                        
                    collected_comments.extend(comments)
                    logger.info(f"已采集 {len(collected_comments)}/{max_comments} 条评论")
                    
                    if not has_more:
                        break
                        
                    cursor = str(len(collected_comments))
                    await asyncio.sleep(1)  # 避免请求过快
                    
                except Exception as e:
                    retries -= 1
                    if retries == 0:
                        raise
                    logger.warning(f"获取评论失败，剩余重试次数: {retries}")
                    await asyncio.sleep(2)
            
            # 处理评论数据
            processed_comments = []
            for comment in collected_comments[:max_comments]:
                processed_comment = self._process_comment(comment)
                if processed_comment:
                    processed_comments.append(processed_comment)
                    
            return processed_comments
                
        except Exception as e:
            logger.error(f"采集评论失败: {str(e)}")
            raise

    def save_comment(self, comment_data, video_id):
        """保存评论数据"""
        try:
            # 将时间戳转换为 datetime 对象
            created_at = datetime.fromtimestamp(
                int(comment_data.get('create_time', 0))
            ) if comment_data.get('create_time') else None
            
            comment = Comment(
                video_id=video_id,
                comment_id=comment_data.get('cid', ''),
                content=comment_data.get('text', ''),
                created_at=created_at,
                likes=comment_data.get('digg_count', 0),
                reply_count=comment_data.get('reply_comment_total', 0),
                user_id=comment_data.get('user', {}).get('uid', ''),
                user_nickname=comment_data.get('user', {}).get('nickname', ''),
                ip_location=comment_data.get('ip_label', '')
            )
            db.session.add(comment)
            db.session.commit()
            return comment
        except Exception as e:
            current_app.logger.error(f"保存评论失败: {str(e)}")
            db.session.rollback()
            raise
            
    def save_comments(self, video_id: str, comments: list):
        """保存评论到数据库"""
        operation_id = f"save_{video_id}_{int(time.time())}"
        logger.info(f"[Operation:{operation_id}] Starting to save {len(comments)} comments for video {video_id}")
        
        try:
            saved_count = 0
            skipped_count = 0
            error_count = 0
            
            for index, comment_data in enumerate(comments, 1):
                try:
                    # 检查评论是否已存在
                    comment_id = comment_data.get("cid")
                    if not comment_id:
                        logger.error(f"[Operation:{operation_id}] Missing comment ID in data: {comment_data}")
                        error_count += 1
                        continue
                        
                    existing = Comment.query.filter_by(comment_id=comment_id).first()
                    if existing:
                        logger.debug(f"[Operation:{operation_id}] Comment {comment_id} already exists")
                        skipped_count += 1
                        continue
                        
                    # 创建新评论
                    comment = self.save_comment(comment_data, video_id)
                    saved_count += 1
                    
                    if index % 10 == 0:  # 每10条评论记录一次进度
                        logger.info(f"[Operation:{operation_id}] Progress: {index}/{len(comments)} comments processed")
                        db.session.commit()  # 定期提交，避免事务过大
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"[Operation:{operation_id}] Error creating comment: {str(e)}")
                    logger.debug(f"[Operation:{operation_id}] Problematic comment data: {comment_data}")
                    continue
                
            db.session.commit()
            logger.info(f"[Operation:{operation_id}] Operation completed - Saved: {saved_count}, Skipped: {skipped_count}, Errors: {error_count}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"[Operation:{operation_id}] Database operation failed: {str(e)}")
            logger.exception(e)
            raise
            
    def _process_comment(self, comment_data: dict) -> dict:
        """处理评论数据，提取需要的字段并进行格式化"""
        try:
            return {
                'comment_id': str(comment_data.get('cid', '')),
                'content': comment_data.get('text', ''),
                'created_at': datetime.fromtimestamp(
                    int(comment_data.get('create_time', 0))
                ).strftime('%Y-%m-%dT%H:%M:%S'),
                'likes': int(comment_data.get('digg_count', 0)),
                'user_id': str(comment_data.get('user', {}).get('uid', '')),
                'user_nickname': comment_data.get('user', {}).get('nickname', ''),
                'ip_location': comment_data.get('ip_label', ''),
                'reply_count': int(comment_data.get('reply_comment_total', 0))
            }
        except Exception as e:
            logger.error(f"处理评论数据时出错: {e}")
            return None 

    async def verify_cookie(self) -> dict:
        """验证 cookie 是否有效"""
        try:
            # 使用一个已知的视频ID进行测试
            test_video_id = "7346152359719996709"
            params = {
                "aweme_id": test_video_id,
                "cursor": "0",
                "count": "1",
                "item_type": "0"
            }
            
            headers = {
                "Cookie": self.cookie,
                "User-Agent": self.user_agent,
                "Referer": f"https://www.douyin.com/video/{test_video_id}",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            
            # 使用 common 函数处理参数和生成签名
            params, headers = common(self.base_url, params, headers)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(self.base_url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status_code") == 0:
                    return {
                        "valid": True,
                        "message": "Cookie 有效",
                        "expires_in": "未知"  # 抖音API不直接提供过期时间
                    }
                else:
                    return {
                        "valid": False,
                        "message": data.get("status_msg", "Cookie 无效"),
                        "expires_in": "0"
                    }
                    
        except Exception as e:
            logger.error(f"验证cookie失败: {str(e)}")
            return {
                "valid": False,
                "message": f"验证失败: {str(e)}",
                "expires_in": "0"
            }

    async def update_cookie(self, new_cookie: str) -> dict:
        """更新 cookie"""
        try:
            # 先验证新 cookie 是否有效
            old_cookie = self.cookie
            self.cookie = new_cookie
            
            verify_result = await self.verify_cookie()
            if verify_result["valid"]:
                # 如果验证成功，保存到文件
                cookie_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookie.txt")
                with open(cookie_file, "w", encoding="utf-8") as f:
                    f.write(new_cookie)
                return {
                    "success": True,
                    "message": "Cookie 更新成功",
                    "verify_result": verify_result
                }
            else:
                # 如果验证失败，恢复旧的 cookie
                self.cookie = old_cookie
                return {
                    "success": False,
                    "message": "新的 Cookie 无效，已保留原有 Cookie",
                    "verify_result": verify_result
                }
                
        except Exception as e:
            logger.error(f"更新cookie失败: {str(e)}")
            self.cookie = old_cookie
            return {
                "success": False,
                "message": f"更新失败: {str(e)}",
                "verify_result": None
            }

    def _convert_cookies_to_string(self, cookies_json: list) -> str:
        """将 JSON 格式的 cookies 转换为字符串格式"""
        try:
            # 过滤出需要的 cookie
            important_cookies = [
                'sessionid', 'sessionid_ss', 'sid_guard', 'sid_tt', 'uid_tt', 
                'uid_tt_ss', 'passport_csrf_token', 'passport_csrf_token_default',
                'ttwid', 's_v_web_id', 'csrf_session_id', 'msToken', 'UIFID'
            ]
            
            cookie_dict = {}
            for cookie in cookies_json:
                name = cookie.get('name')
                value = cookie.get('value')
                if name and value:
                    cookie_dict[name] = value
                    
            # 构建 cookie 字符串
            cookie_parts = []
            for name, value in cookie_dict.items():
                cookie_parts.append(f"{name}={value}")
                
            return '; '.join(cookie_parts)
            
        except Exception as e:
            logger.error(f"转换cookie格式失败: {str(e)}")
            raise ValueError(f"转换cookie格式失败: {str(e)}")

    async def update_cookie_from_json(self, cookies_json: list) -> dict:
        """从 JSON 格式更新 cookie"""
        try:
            # 转换 cookie 格式
            new_cookie = self._convert_cookies_to_string(cookies_json)
            
            # 使用现有的更新方法
            return await self.update_cookie(new_cookie)
                
        except Exception as e:
            logger.error(f"从JSON更新cookie失败: {str(e)}")
            return {
                "success": False,
                "message": f"从JSON更新cookie失败: {str(e)}",
                "verify_result": None
            } 