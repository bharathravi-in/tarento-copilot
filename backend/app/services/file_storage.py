"""
File storage utility for handling document uploads
Manages file storage to disk with proper organization
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileStorageManager:
    """Manages file uploads and storage"""
    
    # Default upload directory - can be configured via environment
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', '/tmp/documents')
    
    @classmethod
    def ensure_upload_dir(cls) -> str:
        """Create upload directory if it doesn't exist"""
        Path(cls.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        return cls.UPLOAD_DIR
    
    @classmethod
    def get_organization_upload_dir(cls, organization_id: str) -> str:
        """Get organization-specific upload directory"""
        org_dir = os.path.join(cls.ensure_upload_dir(), organization_id)
        Path(org_dir).mkdir(parents=True, exist_ok=True)
        return org_dir
    
    @classmethod
    def save_upload(
        cls,
        file_content: bytes,
        file_name: str,
        organization_id: str,
        document_id: str
    ) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content as bytes
            file_name: Original file name
            organization_id: Organization ID
            document_id: Document ID
            
        Returns:
            File path where the file was saved
        """
        try:
            # Get organization directory
            org_dir = cls.get_organization_upload_dir(organization_id)
            
            # Create document-specific directory
            doc_dir = os.path.join(org_dir, document_id)
            Path(doc_dir).mkdir(parents=True, exist_ok=True)
            
            # Save file with original name
            file_path = os.path.join(doc_dir, file_name)
            
            # Write file to disk
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    @classmethod
    def delete_document_files(cls, organization_id: str, document_id: str) -> bool:
        """
        Delete all files for a document
        
        Args:
            organization_id: Organization ID
            document_id: Document ID
            
        Returns:
            True if deletion was successful
        """
        try:
            doc_dir = os.path.join(
                cls.get_organization_upload_dir(organization_id),
                document_id
            )
            
            if os.path.exists(doc_dir):
                shutil.rmtree(doc_dir)
                logger.info(f"Document directory deleted: {doc_dir}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document files: {str(e)}")
            return False
    
    @classmethod
    def file_exists(cls, file_path: str) -> bool:
        """Check if a file exists"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
