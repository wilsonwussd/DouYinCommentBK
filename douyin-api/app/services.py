import httpx
import asyncio
import time
from datetime import datetime
from loguru import logger
from .models import db, Comment
import sys
import os

# 添加 DouyinComments 目录到 Python 路径
douyin_comments_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DouyinComments')
sys.path.append(douyin_comments_dir)

# 切换工作目录到 DouyinComments 目录
os.chdir(douyin_comments_dir)

# 导入 common 模块
from common import common

class CommentService:
    def __init__(self, cookie):
        if not cookie:
            logger.error("Cookie is empty or not set")
            raise ValueError("Cookie is required but not provided")
            
        self.cookie = cookie
        self.base_url = "https://www.douyin.com/aweme/v1/web/comment/list/"
        logger.info(f"CommentService initialized with cookie length: {len(cookie)}")
        logger.debug(f"Base URL: {self.base_url}")
        
    async def fetch_comments(self, video_id: str, cursor: str = "0", count: str = "20"):
        """获取评论数据"""
        start_time = time.time()
        request_id = f"{video_id}_{cursor}_{int(start_time)}"
        logger.info(f"[Request:{request_id}] Starting comment fetch")
        
        if not video_id:
            logger.error(f"[Request:{request_id}] Video ID is empty")
            raise ValueError("Video ID is required")
            
        try:
            params = {
                "aweme_id": video_id,
                "cursor": cursor,
                "count": count,
                "item_type": 0
            }
            headers = {"cookie": self.cookie}
            
            # 使用 common 模块处理参数
            try:
                params, headers = common(self.base_url, params, headers)
                logger.debug(f"[Request:{request_id}] Processed params: {params}")
                logger.debug(f"[Request:{request_id}] Processed headers: {headers}")
            except Exception as e:
                logger.error(f"[Request:{request_id}] Error processing request parameters: {str(e)}")
                raise ValueError(f"签名生成失败: {str(e)}")
            
            # 构建完整的请求 URL
            url = httpx.URL(self.base_url).copy_with(params=params)
            logger.info(f"[Request:{request_id}] Full request URL: {url}")
            
            async with httpx.AsyncClient(timeout=30) as client:
                logger.debug(f"[Request:{request_id}] Sending request...")
                response = await client.get(url, headers=headers)
                response_time = time.time() - start_time
                logger.info(f"[Request:{request_id}] Request completed in {response_time:.2f} seconds")
                
                # 记录响应信息
                logger.debug(f"[Request:{request_id}] Response status code: {response.status_code}")
                logger.debug(f"[Request:{request_id}] Response headers: {dict(response.headers)}")
                logger.debug(f"[Request:{request_id}] Response content length: {len(response.content)}")
                logger.debug(f"[Request:{request_id}] Response content type: {response.headers.get('content-type', 'unknown')}")
                logger.debug(f"[Request:{request_id}] Response content: {response.text[:2000]}...")  # 记录更多的响应内容
                
                # 检查响应状态码
                if response.status_code != 200:
                    logger.error(f"[Request:{request_id}] Request failed with status code: {response.status_code}")
                    logger.error(f"[Request:{request_id}] Response headers: {dict(response.headers)}")
                    logger.error(f"[Request:{request_id}] Response content: {response.text}")
                    response.raise_for_status()
                
                # 检查响应内容是否为空
                if not response.text:
                    logger.error(f"[Request:{request_id}] Empty response received")
                    raise ValueError("Empty response received from server")
                
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f"[Request:{request_id}] Failed to parse JSON response: {str(e)}")
                    logger.error(f"[Request:{request_id}] Response content: {response.text}")
                    raise ValueError(f"Invalid JSON response: {str(e)}")
                
                logger.debug(f"[Request:{request_id}] Response data: {data}")
                
                if data.get("status_code") != 0:
                    error_msg = f"请求失败: {data.get('status_msg', '未知错误')}"
                    logger.error(f"[Request:{request_id}] {error_msg}")
                    logger.error(f"[Request:{request_id}] Full error response: {data}")
                    raise ValueError(error_msg)
                    
                comments = data.get("comments", [])
                has_more = data.get("has_more", 0)
                logger.info(f"[Request:{request_id}] Fetched {len(comments)} comments, has_more: {has_more}")
                
                if comments:
                    logger.debug(f"[Request:{request_id}] First comment preview: {comments[0]}")
                    
                return comments, has_more
                
        except httpx.HTTPError as e:
            logger.error(f"[Request:{request_id}] HTTP error occurred: {str(e)}")
            logger.error(f"[Request:{request_id}] Request URL: {e.request.url if hasattr(e, 'request') else 'Unknown'}")
            logger.error(f"[Request:{request_id}] Request headers: {e.request.headers if hasattr(e, 'request') else 'Unknown'}")
            logger.exception(e)
            raise
        except Exception as e:
            logger.error(f"[Request:{request_id}] Error fetching comments: {str(e)}")
            logger.exception(e)
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
                    comment = Comment(
                        video_id=video_id,
                        comment_id=comment_id,
                        content=comment_data.get("text", "").encode().decode('unicode_escape'),
                        likes=comment_data.get("digg_count", 0),
                        user_nickname=comment_data.get("user", {}).get("nickname", ""),
                        user_id=comment_data.get("user", {}).get("unique_id", ""),
                        ip_location=comment_data.get("ip_label", ""),
                        reply_count=comment_data.get("reply_comment_total", 0),
                        created_at=datetime.fromtimestamp(comment_data.get("create_time", 0))
                    )
                    db.session.add(comment)
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
            
    async def collect_comments(self, video_id: str, max_comments: int = 100):
        """采集指定数量的评论"""
        collection_id = f"collect_{video_id}_{int(time.time())}"
        logger.info(f"[Collection:{collection_id}] Starting comment collection for video {video_id}, max_comments: {max_comments}")
        
        collected_comments = []
        cursor = "0"
        retry_count = 0
        max_retries = 3
        
        try:
            while len(collected_comments) < max_comments:
                try:
                    comments, has_more = await self.fetch_comments(video_id, cursor)
                    retry_count = 0  # 重置重试计数
                    
                    if not comments:
                        logger.info(f"[Collection:{collection_id}] No more comments available")
                        break
                        
                    collected_comments.extend(comments)
                    logger.info(f"[Collection:{collection_id}] Progress: {len(collected_comments)}/{max_comments} comments collected")
                    
                    if not has_more:
                        logger.info(f"[Collection:{collection_id}] No more comments to fetch")
                        break
                        
                    cursor = str(len(collected_comments))
                    logger.debug(f"[Collection:{collection_id}] Waiting before next request, cursor: {cursor}")
                    await asyncio.sleep(1)  # 避免请求过快
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"[Collection:{collection_id}] Max retries reached after {retry_count} attempts")
                        raise
                    logger.warning(f"[Collection:{collection_id}] Retry {retry_count}/{max_retries} after error: {str(e)}")
                    await asyncio.sleep(2 ** retry_count)  # 指数退避
                    
            # 保存到数据库
            if collected_comments:
                logger.info(f"[Collection:{collection_id}] Saving {len(collected_comments)} comments to database")
                self.save_comments(video_id, collected_comments[:max_comments])
                
            logger.info(f"[Collection:{collection_id}] Collection completed successfully")
            return collected_comments[:max_comments]
            
        except Exception as e:
            logger.error(f"[Collection:{collection_id}] Collection failed: {str(e)}")
            logger.exception(e)
            raise 

    def _process_comment(self, comment_data: dict) -> dict:
        """处理评论数据，提取需要的字段并进行格式化"""
        try:
            return {
                'comment_id': str(comment_data.get('cid', '')),
                'content': comment_data.get('text', '').encode().decode('unicode_escape'),  # 解码 Unicode
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