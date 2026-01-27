from enum import Enum


class PDFTemplate(Enum):
    CLASSIC = "classic"
    MODERN = "modern"

    @classmethod
    def list_values(cls):
        return [item.value for item in cls]
