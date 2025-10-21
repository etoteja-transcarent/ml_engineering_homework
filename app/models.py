from pydantic import BaseModel
from typing import Optional


class Form1040Fields(BaseModel):
    """Parsed fields from Form 1040"""
    line_9: float   # Total income
    line_10: float  # Adjustments to income
    line_11: float  # Adjusted gross income (should be line 9 - line 10)
    is_valid: bool  # Whether the math checks out
    
    @classmethod
    def validate_totals(cls, line_9: float, line_10: float, line_11: float) -> bool:
        """Check if line 11 equals line 9 minus line 10"""
        calculated_line_11 = line_9 - line_10
        # Allow small floating point tolerance
        return abs(calculated_line_11 - line_11) < 0.01


class ParseRequest(BaseModel):
    """Request to parse a 1040 document"""
    document_bytes: str  # Base64 encoded document
    

class ParseResponse(BaseModel):
    """Response containing parsed 1040 data"""
    success: bool
    fields: Optional[Form1040Fields] = None
    error: Optional[str] = None

