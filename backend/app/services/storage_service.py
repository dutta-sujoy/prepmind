"""
Supabase Storage Service for file uploads
"""

from typing import Optional
import uuid
from app.config import settings
from app.core.exceptions import BadRequestException


class StorageService:
    """Service for handling file uploads to Supabase Storage"""
    
    def __init__(self):
        self.bucket_name = "resumes"
        self.supabase = None
        self.storage_available = False
        
        try:
            from supabase import create_client
            
            # Use service role key for backend (bypasses RLS)
            api_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None) or settings.SUPABASE_ANON_KEY
            
            if not settings.SUPABASE_URL or not api_key:
                print("⚠️  Supabase credentials not configured")
                return
            
            print(f"🔌 Connecting to Supabase Storage...")
            
            self.supabase = create_client(settings.SUPABASE_URL, api_key)
            
            # Test connection
            buckets = self.supabase.storage.list_buckets()
            
            print(f"   Found {len(buckets)} bucket(s)")
            
            # Check if resumes bucket exists
            bucket_exists = any(b.name == self.bucket_name for b in buckets)
            
            if bucket_exists:
                self.storage_available = True
                print(f"✅ Storage ready! Bucket: {self.bucket_name}")
            else:
                print(f"⚠️  Bucket '{self.bucket_name}' not found")
                
        except Exception as e:
            print(f"⚠️  Storage init failed: {e}")
    
    
    def upload_resume(
        self, 
        file_content: bytes, 
        user_id: uuid.UUID, 
        filename: str
    ) -> str:
        """Upload resume file to Supabase Storage"""
        
        # If storage not available, return local path
        if not self.storage_available or not self.supabase:
            file_ext = filename.split(".")[-1].lower()
            local_path = f"/storage/resumes/{user_id}/{uuid.uuid4()}.{file_ext}"
            print(f"⚠️  Storage not available, using local path")
            return local_path
        
        try:
            # Generate unique filename
            file_ext = filename.split(".")[-1].lower()
            unique_filename = f"{user_id}/{uuid.uuid4()}.{file_ext}"
            
            print(f"📤 Uploading to Supabase...")
            print(f"   Path: {unique_filename}")
            print(f"   Size: {len(file_content)} bytes")
            
            # Upload file to Supabase Storage
            # IMPORTANT: Use upload() method correctly
            result = self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={
                    "content-type": self._get_mime_type(file_ext),
                    "cache-control": "3600",
                }
            )
            
            print(f"✅ Upload successful!")
            print(f"   Result: {result}")
            
            # Get public URL
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(unique_filename)
            
            print(f"🔗 Public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Upload failed!")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            
            # Try to get more details
            if hasattr(e, 'message'):
                print(f"   Message: {e.message}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response}")
            
            # Fallback to local path
            file_ext = filename.split(".")[-1].lower()
            fallback_path = f"/storage/resumes/{user_id}/{uuid.uuid4()}.{file_ext}"
            print(f"⚠️  Using fallback: {fallback_path}")
            return fallback_path
    
    
    def _get_mime_type(self, file_ext: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain"
        }
        return mime_types.get(file_ext.lower(), "application/octet-stream")
    
    
    def delete_resume(self, file_url: str) -> bool:
        """Delete resume file from Supabase Storage"""
        
        if not self.storage_available or not self.supabase:
            return True
        
        # Don't try to delete local paths
        if file_url.startswith("/storage/"):
            return True
        
        try:
            # Extract path from URL
            # URL: https://project.supabase.co/storage/v1/object/public/resumes/user-id/file.pdf
            if "/resumes/" in file_url:
                path = file_url.split("/resumes/")[1]
            else:
                return True
            
            print(f"🗑️  Deleting: {path}")
            
            # Delete file
            self.supabase.storage.from_(self.bucket_name).remove([path])
            
            print(f"✅ Deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    
    def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        if not self.supabase or file_path.startswith("/"):
            return file_path
        return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)


# Singleton instance
storage_service = StorageService()
