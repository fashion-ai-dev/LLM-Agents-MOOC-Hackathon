import json
import os
from typing import List
import requests

from openai_client.connection import OpenAISingleton
from style_agent.taxonomy import Taxonomy, TaxonomyCategoryProperties
from style_agent.schemas import properties_schema, categories_schema
from style_agent.prompts import properties_prompt, categories_sys_prompt


def get_taxonomy(language):
    query = {"language": language}

    taxonomy_response = requests.get(
        f"http://92.112.177.201:8085/vision_taxonomy/",
        params=query,
        headers={"password": os.getenv("TAXONOMY_API_PASSWORD")},
    )

    taxonomy_response_json = taxonomy_response.json()

    taxonomy = taxonomy_response_json["data"]

    return Taxonomy.create(taxonomy)


def get_vision_categories(customer_id: str):
    headers = {
        "accept": "application/json",
        "password": os.getenv("CATALOG_API_TOKEN"),
    }
    url = f"http://147.79.110.30:8080/api/v1/products/pvt/get-vision-categories/customer/{customer_id}"

    response = requests.get(url, headers=headers)

    return response.json()


def get_attributes_text(attributes: List[TaxonomyCategoryProperties]):
    result = ""

    for attribute in attributes:
        result += f"""Group: {attribute.type}\nProperty: {attribute.property}\nDescription: {attribute.description}\nExamples: {attribute.examples}\n"""

    return result


def get_text_characteristic_attributes(taxonomy: Taxonomy):
    result = [
        f"{category.name}:\n{get_attributes_text(category.get_characteristic_attributes())}"
        for category in taxonomy.get_categories()
    ]

    # "Vestido"
    # Group: design_feature\n
    # Property: Percepcao de cor
    # Description: {attribute.description}
    # \nExamples: {attribute.examples}\n

    return "\n".join(result)


async def fashion_input(text, sid, taxonomy_language):
    objeto = ""

    # step 1: quebrar o TEXT como o strategy factory
    taxonomy = get_taxonomy(taxonomy_language)

    taxonomy = taxonomy.get_by_categories_list(get_vision_categories(sid))

    cat_sys = categories_sys_prompt.replace(
        "{{categories}}", ",".join(taxonomy.get_categories_name())
    )

    category_messages = [
        {"role": "system", "content": cat_sys},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text,
                }
            ],
        },
    ]

    response_categories = OpenAISingleton.get_instance().client.chat.completions.create(
        model="gpt-4o-mini",
        messages=category_messages,
        response_format=categories_schema,
        seed=1000,
        temperature=0,
    )

    # Parse response and handle empty case
    category_response = json.loads(response_categories.choices[0].message.content)["response"]
    if not category_response:
        available_categories_text = "all categories are eligible. Focus on comon properties listed below"
        category_attributes_text = "all categories are eligible. Focus on comon properties listed below"
    else:
        taxonomy = taxonomy.get_by_categories_list(category_response)
        available_categories_text = str(taxonomy.get_categories_name())
        category_attributes_text = get_text_characteristic_attributes(taxonomy)

    properties_sys_prompt = (
        properties_prompt.replace("{available_categories}", available_categories_text)
            .replace("{category_attributes}", category_attributes_text)
            .replace("{common_attributes}", get_attributes_text(taxonomy.get_common_attributes()))
    )

    properties_message = [
        {"role": "system", "content": properties_sys_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text,
                }
            ],
        },
    ]

    properties_message = OpenAISingleton.get_instance().client.chat.completions.create(
        model="gpt-4o",
        messages=properties_message,
        response_format=properties_schema,
        seed=1000,
        temperature=0,
    )
    # Criar embeddings
    properties_response = json.loads(properties_message.choices[0].message.content)
    embeddings_list = [
        f"""{' '.join(p["Property"].split("_")).capitalize()}: {p["Value"]} """
        for prop in properties_response["response"][0]["completions"]
        for p in prop["Properties"]
    ] # cor de fundo: preto/Percepcao de cor: preto

    embeddings_result = OpenAISingleton.get_instance().client.embeddings.create(
        input=embeddings_list, model="text-embedding-3-small"
    )

    # Objeto contem os textos processados e também a lista de embeddings
    # Flatten the list of embeddings if any embedding is a list itself
    embeddings = []
    for embed in embeddings_result.data:
        embeddings.append(embed.embedding)

    return {
        "properties_response": properties_message.choices[0].message.content,
        "embeddings": embeddings,
        "categories": [
            prop["Category"]
            for prop in properties_response["response"][0]["completions"]
        ],
    }

