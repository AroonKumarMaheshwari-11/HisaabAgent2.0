"""
Gemini response_schema definitions for structured output.

Kept separate from prompts.py: a schema is a contract about shape, a prompt
is instruction about content. Mixing them makes both harder to change
independently.
"""

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sales": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "number", "nullable": True},
                    "unit_price": {"type": "number", "nullable": True},
                    "cost_price": {"type": "number", "nullable": True},
                },
                "required": ["product_name"],
            },
        },
        "purchases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "number", "nullable": True},
                    "cost_price": {"type": "number", "nullable": True},
                    "selling_price": {"type": "number", "nullable": True},
                },
                "required": ["product_name"],
            },
        },
        "expenses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "amount": {"type": "number", "nullable": True},
                    "notes": {"type": "string", "nullable": True},
                },
                "required": ["category"],
            },
        },
        "receivables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string"},
                    "amount": {"type": "number", "nullable": True},
                    "due_date": {"type": "string", "nullable": True},
                    "notes": {"type": "string", "nullable": True},
                },
                "required": ["customer_name"],
            },
        },
        "payables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "supplier_name": {"type": "string"},
                    "amount": {"type": "number", "nullable": True},
                    "due_date": {"type": "string", "nullable": True},
                    "notes": {"type": "string", "nullable": True},
                },
                "required": ["supplier_name"],
            },
        },
        "clarifications_needed": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["sales", "purchases", "expenses", "receivables", "payables",
                 "clarifications_needed"],
}
