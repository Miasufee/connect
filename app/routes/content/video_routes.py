from  fastapi import  APIRouter

from app.crud.contents_cruds.video_cruds import video_crud

router = APIRouter()

async def create_video_metadata(payload):
    video = video_crud.create()