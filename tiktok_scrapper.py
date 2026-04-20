# tiktok_scrapper.py
import requests
import json
import pandas as pd
import time
import re
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.prompt import Prompt
import pyfiglet

console = Console()

def get_video_id(url):
    """Ekstrak video ID dari URL TikTok"""
    patterns = [
        r'/video/(\d+)',
        r'/(\d+)\?',
        r'/(\d+)$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_comments(video_id, max_comments=1000):
    """Ambil komentar dari TikTok menggunakan API internal"""
    comments_url = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={video_id}&count=20&cursor=0"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': f'https://www.tiktok.com/@user/video/{video_id}'
    }
    
    all_comments = []
    cursor = 0
    has_more = True
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Mengambil komentar...", total=max_comments)
        
        while has_more and len(all_comments) < max_comments:
            try:
                response = requests.get(
                    f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={video_id}&count=20&cursor={cursor}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    comments = data.get('comments', [])
                    
                    for comment in comments:
                        comment_data = {
                            'cid': comment.get('cid'),
                            'username': comment.get('user', {}).get('unique_id', ''),
                            'nickname': comment.get('user', {}).get('nickname', ''),
                            'comment': comment.get('text', ''),
                            'create_time': datetime.fromtimestamp(
                                int(comment.get('create_time', 0))
                            ).strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'digg_count': comment.get('digg_count', 0),
                            'total_reply': comment.get('reply_comment_total', 0),
                            'replies': []
                        }
                        
                        # Ambil balasan komentar jika ada
                        if comment_data['total_reply'] > 0:
                            replies = fetch_replies(video_id, comment.get('cid'), headers)
                            comment_data['replies'] = replies
                        
                        all_comments.append(comment_data)
                        progress.update(task, advance=1)
                    
                    cursor = data.get('cursor', 0)
                    has_more = data.get('has_more', 0) == 1
                else:
                    has_more = False
                    
                time.sleep(1)  # Jeda untuk menghindari rate limit
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                has_more = False
    
    return all_comments

def fetch_replies(video_id, comment_id, headers, max_replies=50):
    """Ambil balasan dari sebuah komentar"""
    replies = []
    cursor = 0
    
    try:
        response = requests.get(
            f"https://www.tiktok.com/api/comment/list/reply/?aid=1988&aweme_id={video_id}&comment_id={comment_id}&cursor={cursor}&count=20",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            for reply in data.get('comments', []):
                reply_data = {
                    'cid': reply.get('cid'),
                    'username': reply.get('user', {}).get('unique_id', ''),
                    'nickname': reply.get('user', {}).get('nickname', ''),
                    'comment': reply.get('text', ''),
                    'create_time': datetime.fromtimestamp(
                        int(reply.get('create_time', 0))
                    ).strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'digg_count': reply.get('digg_count', 0)
                }
                replies.append(reply_data)
                if len(replies) >= max_replies:
                    break
                    
    except Exception as e:
        console.print(f"[yellow]Gagal mengambil balasan: {e}[/yellow]")
    
    return replies

def save_to_excel(comments, video_id):
    """Simpan komentar ke file Excel"""
    flattened_data = []
    
    for comment in comments:
        row = {
            'Username': comment['username'],
            'Nickname': comment['nickname'],
            'Komentar': comment['comment'],
            'Waktu': comment['create_time'],
            'Like': comment['digg_count'],
            'Jumlah Balasan': comment['total_reply'],
            'Tipe': 'Komentar Utama'
        }
        flattened_data.append(row)
        
        for reply in comment['replies']:
            reply_row = {
                'Username': reply['username'],
                'Nickname': reply['nickname'],
                'Komentar': f"↳ {reply['comment']}",  # Indentasi untuk balasan
                'Waktu': reply['create_time'],
                'Like': reply['digg_count'],
                'Jumlah Balasan': 0,
                'Tipe': 'Balasan'
            }
            flattened_data.append(reply_row)
    
    df = pd.DataFrame(flattened_data)
    filename = f"tiktok_comments_{video_id}.xlsx"
    df.to_excel(filename, index=False)
    console.print(f"[green]✅ Data disimpan ke {filename}[/green]")
    return filename

def save_to_json(comments, video_id):
    """Simpan komentar ke file JSON"""
    filename = f"tiktok_comments_{video_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    console.print(f"[green]✅ Data disimpan ke {filename}[/green]")
    return filename

def display_stats(comments):
    """Tampilkan statistik di terminal"""
    table = Table(title="📊 Statistik Komentar")
    table.add_column("Metrik", style="cyan")
    table.add_column("Nilai", style="green")
    
    total_comments = len(comments)
    total_replies = sum(c['total_reply'] for c in comments)
    total_likes = sum(c['digg_count'] for c in comments)
    
    table.add_row("Total Komentar Utama", str(total_comments))
    table.add_row("Total Balasan", str(total_replies))
    table.add_row("Total Interaksi (Like)", str(total_likes))
    
    if total_comments > 0:
        avg_likes = total_likes / total_comments
        table.add_row("Rata-rata Like per Komentar", f"{avg_likes:.2f}")
    
    console.print(table)

def main():
    # Tampilkan banner
    banner = pyfiglet.figlet_format("TikTok Scraper")
    console.print(f"[bold magenta]{banner}[/bold magenta]")
    console.print("[bold yellow]💬 TikTok Comment Scraper - Ambil Semua Komentar & Balasan[/bold yellow]\n")
    
    # Minta URL video
    url = Prompt.ask("[cyan]Masukkan URL video TikTok[/cyan]")
    video_id = get_video_id(url)
    
    if not video_id:
        console.print("[red]❌ Gagal mengekstrak video ID dari URL[/red]")
        return
    
    console.print(f"[green]✅ Video ID: {video_id}[/green]\n")
    
    # Ambil komentar
    comments = fetch_comments(video_id)
    
    if comments:
        # Tampilkan statistik
        display_stats(comments)
        
        # Simpan data
        save_to_json(comments, video_id)
        save_to_excel(comments, video_id)
        
        # Preview beberapa komentar
        console.print("\n[bold]📝 Preview 5 komentar teratas:[/bold]")
        for i, comment in enumerate(comments[:5], 1):
            console.print(f"{i}. @{comment['username']}: {comment['comment'][:100]}...")
    else:
        console.print("[red]❌ Tidak ada komentar yang ditemukan[/red]")

if __name__ == "__main__":
    main()