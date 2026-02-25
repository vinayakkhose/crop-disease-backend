"""
User Model
"""

from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from app.models.schemas import Role

class User:
    """User model"""
    
    def __init__(self, email: str, hashed_password: str, full_name: str,
                 role: Role = Role.FARMER, region: Optional[str] = None,
                 phone: Optional[str] = None, _id: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.id = _id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.region = region
        self.phone = phone
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "role": self.role.value,
            "region": self.region,
            "phone": self.phone,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        # Handle MongoDB ObjectId
        _id = data.get("_id")
        if _id:
            _id = str(_id)
        
        # Handle created_at - ensure it's a datetime
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            from datetime import datetime
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.utcnow()
        
        return cls(
            _id=_id or "",
            email=data["email"],
            hashed_password=data["hashed_password"],
            full_name=data["full_name"],
            role=Role(data.get("role", "farmer")),
            region=data.get("region"),
            phone=data.get("phone"),
            created_at=created_at
        )
