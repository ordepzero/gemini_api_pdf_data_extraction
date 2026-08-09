from pydantic import BaseModel


class UploadFeedback(BaseModel):
    success: bool
    title: str
    message: str
