from pydantic import BaseModel, Field, conint
from typing import Literal, Union

class BaseDownloadRequest(BaseModel):
    max_results: conint(gt=0, le=100) = Field( # type: ignore
        description="Number of shorts to download (1-100)"
    )

class KeywordSearchRequest(BaseDownloadRequest):
    search_type: Literal["keyword"] = Field(
        default="keyword",
        description="Type of search (fixed as 'keyword' for keyword-based search)"
    )
    query: str = Field(
        min_length=1,
        description="Search query for finding YouTube shorts"
    )
    max_results: conint(gt=0, le=100) = Field( # type: ignore
        description="Number of shorts to download (1-100)"
    )

class ChannelSearchRequest(BaseDownloadRequest):
    search_type: Literal["channel"] = Field(
        default="channel",
        description="Type of search (fixed as 'channel' for channel-based search)"
    )
    channel_url: str = Field(
        description="YouTube channel URL, handle (@username), or channel ID"
    )
    max_results: conint(gt=0, le=100) = Field( # type: ignore
        description="Number of shorts to download (1-100)"
    )

# Union type for accepting either type of request
DownloadRequest = Union[KeywordSearchRequest, ChannelSearchRequest]

