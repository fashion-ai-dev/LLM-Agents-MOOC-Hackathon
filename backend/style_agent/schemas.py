properties_schema = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "It is related to which question was answered. It must be the exact question that was responded",
                            },
                            "completions": {
                                "type": "array",
                                "description": "Here will be placed the examples that match the user query",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Category": {
                                            "type": "string",
                                            "description": "Named categories lilsted on **Available categories:**. If all categories are available pass a empty string",
                                        },
                                        "Properties": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "Property": {
                                                        "type": "string",
                                                        "description": "The type of property. Do NOT translate, keep original.",
                                                    },
                                                    "Value": {
                                                        "type": "string",
                                                        "description": "The value for the property. Translate the value.",
                                                    },
                                                    "Group": {
                                                        "type": "string",
                                                        "description": "To witch group of properties this property is in",
                                                    },
                                                },
                                                "required": [
                                                    "Property",
                                                    "Value",
                                                ],
                                                "additionalProperties": False,
                                            },
                                        },
                                    },
                                    "required": ["Category", "Properties"],
                                    "additionalProperties": False,
                                },
                            },
                            "negatives": {
                                "type": "array",
                                "description": "Here will be placed all examples that the user does not want",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Category": {
                                            "type": "string",
                                            "description": "The category name. Do NOT translate, keep original.",
                                        },
                                        "Properties": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "Property": {
                                                        "type": "string",
                                                        "description": "The type of property. Do NOT translate, keep original.",
                                                    },
                                                    "Value": {
                                                        "type": "string",
                                                        "description": "The value for the property. Translate the value.",
                                                    },
                                                    "Group": {
                                                        "type": "string",
                                                        "description": "To witch group of properties this property is in",
                                                    },
                                                },
                                                "required": [
                                                    "Property",
                                                    "Value",
                                                ],
                                                "additionalProperties": False,
                                            },
                                        },
                                    },
                                    "required": ["Category", "Properties"],
                                    "additionalProperties": False,
                                },
                            },
                        },
                        "explanation": {
                            "type": "string",
                            "description": """Explain in the most detailed way why these properties were selected. Your response must include:

                                1. **Step-by-step reasoning**: Describe the decision-making process in chronological order, from data analysis to the final choice.
                                2. **Criteria used**: Explain the factors that influenced the selection, such as relevance, statistical patterns, business logic, or prior knowledge.
                                3. **Comparison with alternatives**: List other potential properties that were considered but rejected, along with the reasons for their exclusion.
                                4. **Relationships between properties**: Explain how the selected properties interact and contribute to the overall objective.
                                5. **Impact of each property**: Describe the specific role of each property and how it aligns with the intended outcome.
                                6. **Confidence level**: If applicable, provide the confidence level of the decision and any potential areas of uncertainty.

                                Ensure your response is structured and well-organized to provide maximum clarity.
                                """,
                        },
                        "required": ["negatives", "question", "completions"],
                    },
                },
            },
        },
        "name": "category_properties_response",
    },
}

categories_schema = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Categories identified on user input.",
                    },
                }
            },
        },
        "name": "category_schema",
    },
}
