"""Example database model.

This is a sample model to demonstrate the structure.
Replace with your actual models.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ExampleModel(Base):
    """Example model for demonstration purposes.
    
    This model includes common fields you might need:
    - id, created_at, updated_at (inherited from Base)
    - title, description, status (defined here)
    
    Modify or delete this model based on your service needs.
    """
    
    __tablename__ = "examples"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
    )
    
    def __repr__(self) -> str:
        return f"<ExampleModel(id={self.id}, title='{self.title}', status='{self.status}')>"
