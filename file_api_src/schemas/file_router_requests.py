from pydantic import BaseModel
from fastapi import UploadFile, File, Form


class FileCreationRequest(BaseModel):
    file: UploadFile
    folder_id: int

    @classmethod
    def as_form(
            cls,
            file: UploadFile = File(..., description="Binary data of file"),
            folder_id: int = Form(..., description="ID of the folder"),
    ):
        return cls(file=file, folder_id=folder_id)

