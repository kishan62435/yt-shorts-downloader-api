from fastapi import APIRouter, Depends
import app.api.v1.dependencies.auth
from app.api.v1.dependencies.auth import get_current_user
from app.core.mainScript import startDownload
from app.schemas.downloadParams import KeywordSearchRequest, ChannelSearchRequest
from typing import Union


router = APIRouter()

#Download video (protcted)

@router.post("/download")
async def download_video(request: Union[KeywordSearchRequest, ChannelSearchRequest], current_user: dict = Depends(get_current_user)):

    # return {"success": True, "message": "Video downloaded successfully", "video_urls": [
    #     "/videosList/Ben_Lionel_Scott/1_ENvgK0mPpqg_combined.mp4"
    # ]}

    try:
        search_type = ""
        params = {}
        if request.search_type == "keyword":
            # Handle keyword search
            print(f"here is the keyword request:{request}")
            search_type = "keyword"
            params.update({"query": request.query, "max_results": request.max_results})
            # return {"message": "Keyword search"}
        else:
            print(f"here is the channel request:{request}")
            search_type = "channel"
            params.update({"channel_url": request.channel_url, "max_results": request.max_results})
            # return {"message": "channel search"}
        
            # return {"status": "processing", "request": request.dict()}
        print(f"here is the search type and params from video.py: {search_type}, {params}")

        video_urls = startDownload(search_type, params)
        return {"success": True, "message": "Video downloaded successfully", "video_urls": video_urls}
    except Exception as e:
        print(f"Error parsing request: {str(e)} in the api video.py")
        return {"success": False, "message": f"Error parsing request: {str(e)}"}

