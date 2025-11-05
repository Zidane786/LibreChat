"""
File routes for upload, download, and management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from fastapi.responses import FileResponse
from app.schemas.file import (
    FileUploadResponse,
    FileResponse as FileResponseSchema,
    DeleteFilesRequest,
    FileConfigResponse,
)
from app.services.file_service import FileService
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger
from app.config import get_settings

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/", response_model=List[FileResponseSchema])
async def get_files(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all files for the current user.
    """
    try:
        file_service = FileService()
        files = await file_service.get_user_files(current_user.id)
        return [FileResponseSchema(**file.dict()) for file in files]

    except Exception as e:
        logger.error(f"Error getting files: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in request: {str(e)}",
        )


@router.get("/agent/{agent_id}", response_model=List[FileResponseSchema])
async def get_agent_files(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get files specific to an agent.
    """
    try:
        if not agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent ID is required",
            )

        file_service = FileService()
        files = await file_service.get_agent_files(agent_id)
        return [FileResponseSchema(**file.dict()) for file in files]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent files",
        )


@router.get("/config", response_model=FileConfigResponse)
async def get_file_config(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get file configuration.
    """
    try:
        settings = get_settings()
        return FileConfigResponse(
            endpoints={},
            serverFileSizeLimit=settings.file_size_limit or 20 * 1024 * 1024,  # 20MB default
            avatarSizeLimit=settings.avatar_size_limit or 2 * 1024 * 1024,  # 2MB default
        )

    except Exception as e:
        logger.error(f"Error getting fileConfig: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in request: {str(e)}",
        )


@router.post("/", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a file.
    """
    try:
        file_service = FileService()
        settings = get_settings()

        # Use file strategy from settings
        source = getattr(settings, 'file_strategy', 'local') or 'local'

        uploaded_file = await file_service.upload_file(
            user_id=current_user.id,
            file=file,
            source=source,
        )

        return FileUploadResponse(
            file_id=uploaded_file.file_id,
            filename=uploaded_file.filename,
            filepath=uploaded_file.filepath,
            bytes=uploaded_file.bytes,
            type=uploaded_file.type,
            width=uploaded_file.width,
            height=uploaded_file.height,
            source=uploaded_file.source,
        )

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}",
        )


@router.post("/images", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload an image file.
    """
    try:
        # Validate image type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image",
            )

        file_service = FileService()
        settings = get_settings()
        source = getattr(settings, 'file_strategy', 'local') or 'local'

        uploaded_file = await file_service.upload_file(
            user_id=current_user.id,
            file=file,
            source=source,
        )

        return FileUploadResponse(
            file_id=uploaded_file.file_id,
            filename=uploaded_file.filename,
            filepath=uploaded_file.filepath,
            bytes=uploaded_file.bytes,
            type=uploaded_file.type,
            width=uploaded_file.width,
            height=uploaded_file.height,
            source=uploaded_file.source,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}",
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Download a file.
    """
    try:
        file_service = FileService()
        file_path = await file_service.get_file_path(current_user.id, file_id)

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        file_record = await file_service.get_file(current_user.id, file_id)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        return FileResponse(
            path=file_path,
            filename=file_record.filename,
            media_type=file_record.type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file",
        )


@router.delete("/")
async def delete_files(
    request: DeleteFilesRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete files.
    """
    try:
        if not request.files or len(request.files) == 0:
            return {"message": "Nothing provided to delete"}

        # Extract file IDs
        file_ids = [f.get('file_id') for f in request.files if f.get('file_id')]

        if not file_ids:
            return {"message": "No valid file IDs provided"}

        file_service = FileService()
        result = await file_service.delete_files(
            user_id=current_user.id,
            file_ids=file_ids,
        )

        return {"message": "Files deleted successfully", **result}

    except Exception as e:
        logger.error(f"Error deleting files: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in request: {str(e)}",
        )
