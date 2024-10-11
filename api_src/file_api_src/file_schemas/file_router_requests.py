from pydantic import BaseModel, UUID4
from fastapi import UploadFile, File, Form


class FileCreationRequest(BaseModel):
    file: UploadFile
    folder_id: int

    @classmethod
    def as_form(
            cls,
            file: UploadFile = File(..., description="Данные о загруженном файле"),
            folder_id: int = Form(..., description="ID папки, куда надо загрузить файл"),
    ):
        return cls(file=file, folder_id=folder_id)


class FolderCreationRequest(BaseModel):
    name: str
    parent_id: UUID4 | None = None
    created_by: str = "admin"

    @classmethod
    def as_form(
            cls,
            name: str = Form(..., description="Имя папки"),
            parent_id: UUID4 | None = Form(None, description="ID родительской папки"),
            created_by: str = Form("admin", description="Кем была создана папка")
    ):
        return cls(name=name, parent_id=parent_id, created_by=created_by)
