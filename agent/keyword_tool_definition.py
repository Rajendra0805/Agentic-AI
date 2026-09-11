SEARCH_KEYWORD_TOOL = {
    "type": "function",
    "function": {
        "name": "search_keyword",
        "description": (
            "Perform an exact, case-insensitive "
            "keyword search in the uploaded document. "
            "Use this tool when the user asks whether "
            "a word or phrase exists, how many times it "
            "appears, or which pages contain it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "The exact word or phrase "
                        "to search for."
                    )
                }
            },
            "required": ["keyword"]
        }
    }
}