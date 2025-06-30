import os
import json
import yt_dlp
from urllib.parse import urlparse, parse_qs
import re

cookies_path = '/home/ubuntu/.yt-dlp/cookies.txt'
def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    # Remove invalid characters and replace spaces with underscores
    return re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')


# Custom exceptions
class YoutubeDownloaderError(Exception):
    """Base exception class for YouTube downloader errors"""
    pass

class InvalidChannelError(YoutubeDownloaderError):
    """Raised when the channel URL/name is invalid"""
    pass

class NoVideosFoundError(YoutubeDownloaderError):
    """Raised when no videos are found"""
    pass

class DownloadError(YoutubeDownloaderError):
    """Raised when video download fails"""
    pass

def get_channel_name(channel_url):
    """Get channel name for folder creation."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            channel_name = info.get('uploader') or info.get('channel') or info.get('title')
            if channel_name:
                return sanitize_filename(channel_name)
    except Exception as e:
        print(f"Warning: Couldn't get channel name: {str(e)}")
        raise InvalidChannelError(f"Invalid channel name")
    
    # return "unknown_channel"
    raise InvalidChannelError("Could not get channel name")

def load_downloaded_ids(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return set(json.load(f))
    return set()

def save_downloaded_id(video_id, json_path):
    downloaded_ids = load_downloaded_ids(json_path)
    downloaded_ids.add(video_id)
    with open(json_path, 'w') as f:
        json.dump(list(downloaded_ids), f)

def extract_channel_identifier(channel_url):
    """Extract channel ID or handle from various YouTube URL formats."""
    parsed_url = urlparse(channel_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    
    if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
        if len(path_parts) >= 2 and path_parts[0] == 'channel':
            return path_parts[1], 'id'
        elif len(path_parts) >= 2 and path_parts[0] == 'c':
            return path_parts[1], 'c'
        elif len(path_parts) >= 1 and path_parts[0].startswith('@'):
            return path_parts[0], 'handle'
        elif len(path_parts) >= 2 and path_parts[0] == 'user':
            return path_parts[1], 'user'
    
    return channel_url, 'unknown'

def get_channel_url(identifier, type_):
    """Convert channel identifier to the appropriate URL format."""
    if type_ == 'id':
        return f"https://www.youtube.com/channel/{identifier}"
    elif type_ == 'c':
        return f"https://www.youtube.com/c/{identifier}"
    elif type_ == 'handle':
        return f"https://www.youtube.com/{identifier}"
    elif type_ == 'user':
        return f"https://www.youtube.com/user/{identifier}"
    else:
        return identifier

def setup_download_directory(base_path, channel_info=None):
    """Setup download directory and return paths."""
    json_path = os.path.join(os.path.dirname(__file__), 'downloadedVideoIds.json')
    if not channel_info:
        download_path = base_path
        # json_path = os.path.join(base_path, 'downloadedVideoIds.json')
    else:
        identifier, type_ = channel_info
        channel_url = get_channel_url(identifier, type_)
        channel_name = get_channel_name(channel_url)
        download_path = os.path.join(base_path, channel_name)
        # json_path = os.path.join(download_path, 'downloadedVideoIds.json')
    
    os.makedirs(download_path, exist_ok=True)
    return download_path, json_path


def search_shorts_page(query, page_size, downloaded_ids, page=1, channel_info=None):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'format': 'best',
    }

    start_idx = (page - 1) * page_size
    
    if channel_info:
        identifier, type_ = channel_info
        channel_url = get_channel_url(identifier, type_)
        search_query = f"{channel_url}/shorts"
    else:
        search_query = f"ytsearch{start_idx + page_size}:{query} shorts"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(search_query, download=False)
            
            if not search_results.get('entries'):
                return []
            
            entries = search_results['entries']
            if not channel_info:
                entries = entries[start_idx:]
            else:
                entries = entries[start_idx:start_idx + page_size]
            
            if channel_info:
                entries = [entry for entry in entries if 'shorts' in entry.get('url', '').lower()]
            
            return [entry['id'] for entry in entries if entry['id'] not in downloaded_ids]
            
        except Exception as e:
            print(f"Error searching videos: {str(e)}")
            return []

def find_unique_videos(query, required_count, downloaded_ids, channel_info=None, max_attempts=10):
    unique_videos = []
    page = 1
    page_size = 50
    attempts = 0

    print("Searching for videos...")
    search_type = "channel" if channel_info else "query"
    print(f"Search type: {search_type}")
    
    while len(unique_videos) < required_count and attempts < max_attempts:
        print(f"Searching page {page}...")
        new_videos = search_shorts_page(query, page_size, downloaded_ids, page, channel_info)
        
        if not new_videos and page == 1:
            raise NoVideosFoundError("No videos found matching the search criteria")
            # print("No more videos found in search results.")
            # break
            
        if not new_videos:
            break
        unique_videos.extend(new_videos)
        unique_videos = list(dict.fromkeys(unique_videos))
        
        print(f"Found {len(unique_videos)}/{required_count} unique videos")
        page += 1
        attempts += 1
        
    return unique_videos[:required_count]

# [Previous download functions remain the same]
def download_combined(video_id, output_path, index, json_path):
    url = f"https://www.youtube.com/shorts/{video_id}"
    ydl_opts = {
        'format': 'best',
        # 'outtmpl': os.path.join(output_path, f'{index}_combined.%(ext)s'),
        'outtmpl': os.path.join(output_path, f'{index}_{video_id}_combined.%(ext)s'),
        'no_warnings': True,
        'ignoreerrors': True,
        
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Downloaded combined video {index}")
            save_downloaded_id(video_id, json_path)
            # return True
            relative_path = os.path.relpath(output_path, os.path.join(os.getcwd(), "videos"))
            video_url = f"/videosList/{f'{relative_path}/{index}_{video_id}_combined'}.mp4"  # Assuming mp4 extension, modify based on the actual file type
            return video_url
    except Exception as e:
        raise DownloadError(f"Error downloading video {index}: {str(e)}")
        # print(f"Error downloading combined video {index}: {str(e)}")
        # return False





def startDownload(search_type, params):
    try: 
        print(f"here is the search type and params: {search_type}, {params}")
        # return
        # search_type = input("Enter search type (1 for keyword search, 2 for channel search): ")

        
        
        channel_info = None
        query = ""
        
        if search_type == "channel":
            # channel_url = input("Enter the channel URL (can be channel URL, @handle, or channel ID): ")
            channel_url = params["channel_url"]
            print("Extracting channel information...")
            identifier, type_ = extract_channel_identifier(channel_url)
            channel_info = (identifier, type_)
            print(f"Successfully extracted channel identifier: {identifier} (type: {type_})")
        else:
            # query = input("Enter your search query: ")
            query = params["query"]
        
        # max_results = int(input("Enter the number of Shorts to download: "))
        max_results = params["max_results"]
        # base_path = os.getcwd()
        base_path = os.path.join(os.getcwd(), "videos")
        # base_path = input("Enter the output directory path: ")
        # download_mode = input("Enter download mode (1 for combined, 2 for separate audio/video): ")
        download_mode = "1"

        # Setup directory structure and get paths
        download_path, json_path = setup_download_directory(base_path, channel_info)
        print(f"Downloads will be saved to: {download_path}")
        
        downloaded_ids = load_downloaded_ids(json_path)
        print(f"Found {len(downloaded_ids)} previously downloaded videos")
        
        video_ids = find_unique_videos(query, max_results, downloaded_ids, channel_info)

        if not video_ids:
            raise NoVideosFoundError("No new videos found!")
            # print("No new videos found!")
            # return

        print(f"\nFound {len(video_ids)} new videos to download")
        
        successful_downloads = 0
        video_urls = [] 
        for index, video_id in enumerate(video_ids, start=1):
            print(f"\nDownloading video {index}/{len(video_ids)}...")
            success = False
            
            if download_mode == "1":
                success = download_combined(video_id, download_path, index, json_path)
                if success:
                    video_urls.append(success)
                
            if success:
                successful_downloads += 1

        if not video_urls:
            raise DownloadError("Failed to download any videos")
        print(f"\nDownload complete! Successfully downloaded {successful_downloads} new videos")
        print(f"Files are saved in: {download_path}")
        return video_urls

    except YoutubeDownloaderError as e:
        # Re-raise the custom exceptions to be caught by the API
        raise
    except Exception as e:
        print(f"Error: {str(e)} printing exception")
        raise YoutubeDownloaderError(f"Unexpected error occured!")
        
# if __name__ == "__main__":
#     main()