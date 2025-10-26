from pydantic import BaseModel,Field
from typing import Optional, Dict, Any

class Form1040DynamicFields(BaseModel):
    """Class to hold dynamic fields for Form 1040, including and beyond lines 11 through 13"""
    fields: dict = Field(default_factory=dict)

    @classmethod
    def add_field(cls, instance: "Form1040DynamicFields", key: str, value: Any) -> None:
        """Add or update a field in the dynamic fields dictionary"""
        instance.fields[key] = value
        

    @classmethod
    def get_field(cls, instance: "Form1040DynamicFields", key: str) -> Optional[Any]:
        """Retrieve a line value if it exists, otherwise retrieve None"""
        return instance.fields.get(key)
    
    @classmethod
    # Changed method name
    def validate_line_11_totals(cls, instance: "Form1040DynamicFields") -> bool:
        """Validating line 11 totals"""
        line_9 = cls.get_field(instance, "line_9")
        line_10 = cls.get_field(instance, "line_10")
        line_11 = cls.get_field(instance, "line_11")
        if line_9 is None or line_10 is None or line_11 is None:
            return False
        calculated_line_11 = line_9 - line_10
        # Allow small floating point tolerance
        return abs(calculated_line_11 - line_11) < 0.01
    
    @classmethod
    def validate_line_14_totals(cls, instance: "Form1040DynamicFields") -> bool:
        """Validating line 14 totals"""
        line_12 = cls.get_field(instance, "line_12")
        line_13 = cls.get_field(instance, "line_13")
        line_14 = cls.get_field(instance, "line_14")
        # As far as I understand, lines 12 and 13 can be left blank, but line 14 must be present to validate
        line_12 = line_12 if line_12 is not None else 0.0
        line_13 = line_13 if line_13 is not None else 0.0
        if line_14 is None:
            return False
        calculated_line_14 = line_12 + line_13
        # Allow small floating point tolerance
        return abs(calculated_line_14 - line_14) < 0.01


class ParseRequest(BaseModel):
    """Parsing 1040 document"""
    document_bytes: str  # Base64 encoded document
    

class ParseResponse(BaseModel):
    """Response containing parsed 1040 data"""
    # Originally "fields: Optional[Form1040DynamicFields] = None" 
    # Had issues with testing because of nested "fields"
    # Did not want to refactor existing tests
    success: bool
    fields: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: Optional[str] = None