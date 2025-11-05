"""
File service for upload/download and storage management.
"""
import os
import uuid
import aiofiles
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from app.models.file import File
from app.config import get_settings
from app.utils.logger import logger


class FileService:
    """Service for managing file uploads and storage."""

    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.file_upload_path or "/app/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def get_user_files(self, user_id: str) -> List[File]:
        """
        Get all files for a user.

        Args:
            user_id: User ID

        Returns:
            List of files
        """
        files = await File.find(File.user == user_id).to_list()
        return files

    async def get_agent_files(self, agent_id: str) -> List[File]:
        """
        Get files attached to an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of files
        """
        # TODO: Query agent tool_resources to get file IDs
        # For now return empty list
        return []

    async def upload_file(
        self,
        user_id: str,
        file: UploadFile,
        source: str = "local",
    ) -> File:
        """
        Upload a file.

        Args:
            user_id: User ID
            file: Uploaded file
            source: Storage source (local, s3, azure_blob)

        Returns:
            Created file record
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Clean filename
        filename = file.filename or "unnamed"
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ".-_ ")

        # Determine storage path
        if source == "local":
            filepath = await self._store_local(file_id, safe_filename, file)
        elif source == "s3":
            filepath = await self._store_s3(file_id, safe_filename, file)
        elif source == "azure_blob":
            filepath = await self._store_azure(file_id, safe_filename, file)
        else:
            raise ValueError(f"Unsupported storage source: {source}")

        # Get file size
        file_size = 0
        if hasattr(file, 'size'):
            file_size = file.size
        else:
            # Read file to get size
            content = await file.read()
            file_size = len(content)
            await file.seek(0)

        # Create file record
        file_record = File(
            file_id=file_id,
            user=user_id,
            filename=safe_filename,
            filepath=filepath,
            source=source,
            type=file.content_type or "application/octet-stream",
            bytes=file_size,
        )
        await file_record.insert()

        logger.info(f"File uploaded: {file_id} ({safe_filename}) for user {user_id}")
        return file_record

    async def _store_local(
        self,
        file_id: str,
        filename: str,
        file: UploadFile,
    ) -> str:
        """Store file locally."""
        file_path = self.upload_dir / f"{file_id}_{filename}"

        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        return str(file_path)

    async def _store_s3(
        self,
        file_id: str,
        filename: str,
        file: UploadFile,
    ) -> str:
        """Store file in S3."""
        # TODO: Implement S3 upload using boto3
        logger.warning("S3 storage not implemented, falling back to local")
        return await self._store_local(file_id, filename, file)

    async def _store_azure(
        self,
        file_id: str,
        filename: str,
        file: UploadFile,
    ) -> str:
        """Store file in Azure Blob Storage."""
        # TODO: Implement Azure Blob upload
        logger.warning("Azure Blob storage not implemented, falling back to local")
        return await self._store_local(file_id, filename, file)

    async def get_file(
        self,
        user_id: str,
        file_id: str,
    ) -> Optional[File]:
        """
        Get a file by ID.

        Args:
            user_id: User ID
            file_id: File ID

        Returns:
            File or None
        """
        return await File.find_one(
            File.file_id == file_id,
            File.user == user_id,
        )

    async def delete_files(
        self,
        user_id: str,
        file_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Delete files.

        Args:
            user_id: User ID
            file_ids: List of file IDs

        Returns:
            Deletion result
        """
        deleted_count = 0

        for file_id in file_ids:
            file_record = await File.find_one(
                File.file_id == file_id,
                File.user == user_id,
            )

            if file_record:
                # Delete physical file
                if file_record.source == "local":
                    try:
                        if os.path.exists(file_record.filepath):
                            os.remove(file_record.filepath)
                    except Exception as e:
                        logger.error(f"Error deleting file {file_record.filepath}: {e}")

                # Delete record
                await file_record.delete()
                deleted_count += 1

        logger.info(f"Deleted {deleted_count} files for user {user_id}")
        return {"deleted": deleted_count, "total": len(file_ids)}

    async def get_file_path(
        self,
        user_id: str,
        file_id: str,
    ) -> Optional[str]:
        """
        Get the physical file path for download.

        Args:
            user_id: User ID
            file_id: File ID

        Returns:
            File path or None
        """
        file_record = await self.get_file(user_id, file_id)
        if not file_record:
            return None

        # For local files, return path directly
        if file_record.source == "local":
            return file_record.filepath if os.path.exists(file_record.filepath) else None

        # For S3/Azure, would need to generate signed URL
        # TODO: Implement signed URL generation
        return None
