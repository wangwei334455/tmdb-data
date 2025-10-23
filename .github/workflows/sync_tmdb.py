#!/usr/bin/env python3
"""
GitHub Actions TMDB数据同步脚本
在GitHub服务器上运行，下载TMDB数据并提交到仓库
"""

import requests
import json
import os
from datetime import datetime, timezone

# TMDB API配置
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
TMDB_BEARER_TOKEN = os.environ.get('TMDB_BEARER_TOKEN')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def download_tmdb_endpoint(endpoint, filename):
    """下载单个TMDB端点数据"""
    headers = {
        'Authorization': f'Bearer {TMDB_BEARER_TOKEN}',
        'Accept': 'application/json',
        'User-Agent': 'HappyTube-GitHub-Sync/1.0'
    }
    
    params = {
        'language': 'zh-CN',
        'page': 1
    }
    
    url = f"{TMDB_BASE_URL}{endpoint}"
    
    try:
        print(f"📡 下载: {endpoint}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        # 保存数据
        filepath = os.path.join('data', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        results_count = len(data.get('results', []))
        print(f"✅ 成功: {filename} ({results_count} 条记录)")
        
        return True, results_count
        
    except requests.RequestException as e:
        print(f"❌ 网络错误 {endpoint}: {e}")
        return False, 0
    except Exception as e:
        print(f"❌ 处理错误 {endpoint}: {e}")
        return False, 0

def main():
    """主函数"""
    print("🎬 GitHub Actions TMDB数据同步")
    print("=" * 50)
    print(f"开始时间: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # 检查API凭据
    if not TMDB_API_KEY or not TMDB_BEARER_TOKEN:
        print("❌ 缺少TMDB API凭据")
        exit(1)
    
    # 要下载的端点
    endpoints = [
        ('/movie/popular', 'movies_popular_page1.json'),
        ('/movie/top_rated', 'movies_top_rated_page1.json'),
        ('/movie/now_playing', 'movies_now_playing_page1.json'),
        ('/tv/popular', 'tv_popular_page1.json'),
        ('/tv/top_rated', 'tv_top_rated_page1.json'),
    ]
    
    # 下载统计
    total_files = len(endpoints)
    success_count = 0
    total_records = 0
    
    # 下载所有端点
    for endpoint, filename in endpoints:
        success, records = download_tmdb_endpoint(endpoint, filename)
        if success:
            success_count += 1
            total_records += records
    
    # 生成更新信息
    update_info = {
        "last_update": datetime.now(timezone.utc).isoformat(),
        "total_files": total_files,
        "success_files": success_count,
        "total_records": total_records,
        "files": [filename for _, filename in endpoints],
        "api_status": "success" if success_count > 0 else "failed"
    }
    
    # 保存更新信息
    os.makedirs('data', exist_ok=True)
    with open('data/update_info.json', 'w', encoding='utf-8') as f:
        json.dump(update_info, f, ensure_ascii=False, indent=2)
    
    # 生成简单的更新时间文件
    with open('data/last_update.txt', 'w') as f:
        f.write(f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Success: {success_count}/{total_files} files\n")
        f.write(f"Total records: {total_records}\n")
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"✅ 同步完成: {success_count}/{total_files} 个文件")
    print(f"📊 总记录数: {total_records}")
    print(f"🕒 完成时间: {datetime.now(timezone.utc).isoformat()}")
    
    if success_count == 0:
        print("❌ 所有下载都失败了")
        exit(1)
    elif success_count < total_files:
        print("⚠️ 部分下载失败")
        exit(0)
    else:
        print("🎉 全部下载成功")
        exit(0)

if __name__ == "__main__":
    main()
