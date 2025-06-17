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

    taxonomy = taxonomy.get_by_categories_list(
        json.loads(response_categories.choices[0].message.content)["response"]
    )

    properties_sys_prompt = (
        properties_prompt.replace(
            "{available_categories}", str(taxonomy.get_categories_name())
        )
        .replace(
            "{category_attributes}",
            get_text_characteristic_attributes(taxonomy),
        )
        .replace(
            "{common_attributes}",
            get_attributes_text(taxonomy.get_common_attributes()),
        )
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


{
    "response": [
        {
            "question": "Peças confortáveis para curtir um dia em casa. Considere apenas feminino adulto",
            "completions": [
                {
                    "Category": "Calças",
                    "Properties": [
                        {
                            "Property": "estilo_de_perna",
                            "Value": "Reta, Cenoura, Alladin, Saruel",
                            "Group": "design_features",
                        },
                        {
                            "Property": "altura_perna",
                            "Value": "Longa, Cropped, Corsario",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_cintura",
                            "Value": "Alta, Clochard, Média, Baixa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "tipo_de_fechamento",
                            "Value": "Elástico, Amarração",
                            "Group": "design_features",
                        },
                        {
                            "Property": "detalhe_da_cintura",
                            "Value": "Elástico, Amarraçao",
                            "Group": "design_features",
                        },
                        {
                            "Property": "barra",
                            "Value": "Bainha Aplicada, Bainha dobrada, Sem bainha",
                            "Group": "design_features",
                        },
                        {
                            "Property": "bolso",
                            "Value": "Sim",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
                {
                    "Category": "Cardigan",
                    "Properties": [
                        {
                            "Property": "caimento",
                            "Value": "Solto, Fluído",
                            "Group": "design_features",
                        },
                        {
                            "Property": "comprimento",
                            "Value": "Regular, Longo",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_das_mangas",
                            "Value": "Manga regular",
                            "Group": "design_features",
                        },
                        {
                            "Property": "comprimento_das_mangas",
                            "Value": "Manga Longa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "tipo_de_fechamento",
                            "Value": "Sem Botões, Sweater",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_barra",
                            "Value": "Barra Reta, Barra Canelada",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caracteristicas_funcionais",
                            "Value": "Bolsos, Tricot",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
                {
                    "Category": "Camisetas",
                    "Properties": [
                        {
                            "Property": "silhueta",
                            "Value": "Regular, Justa, Quadrada, Oversized, Cropped",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caimento",
                            "Value": "Solto, Regular, Relaxado",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_do_decote",
                            "Value": "Gola Redonda, Decote em V, Decote U",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_das_mangas",
                            "Value": "Montada, Ombro Caído",
                            "Group": "design_features",
                        },
                        {
                            "Property": "comprimento_das_mangas",
                            "Value": "Manga Curta, Manga Longa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_barra",
                            "Value": "Barra Reta, Barra Curva",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caracteristicas_funcionais",
                            "Value": "Bolsos",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
                {
                    "Category": "Shorts",
                    "Properties": [
                        {
                            "Property": "estilo_de_short",
                            "Value": "Running, Alfaiatraia, Evase, Reto",
                            "Group": "design_features",
                        },
                        {
                            "Property": "altura_perna",
                            "Value": "Curto",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_cintura",
                            "Value": "Alta, Clochard, Média, Baixa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "tipo_de_fechamento",
                            "Value": "Elástico, Amarração",
                            "Group": "design_features",
                        },
                        {
                            "Property": "detalhe_da_cintura",
                            "Value": "Elástico, Amarraçao",
                            "Group": "design_features",
                        },
                        {
                            "Property": "barra",
                            "Value": "Bainha Aplicada, Bainha dobrada, Sem bainha",
                            "Group": "design_features",
                        },
                        {
                            "Property": "bolso",
                            "Value": "Sim",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
                {
                    "Category": "Suéter",
                    "Properties": [
                        {
                            "Property": "silhueta",
                            "Value": "Regular, Ajustado, Quadrado, Oversized, Cropped, Longo",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caimento",
                            "Value": "Solto, Regular, Relaxado",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_do_decote",
                            "Value": "Gola Redonda, Decote em V, Gola Alta",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_das_mangas",
                            "Value": "Montada, Ombro Caído",
                            "Group": "design_features",
                        },
                        {
                            "Property": "comprimento_das_mangas",
                            "Value": "Manga Longa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_barra",
                            "Value": "Barra Reta, Barra Canelada",
                            "Group": "design_features",
                        },
                        {
                            "Property": "elementos_decorativos",
                            "Value": "Bolsos",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caracteristicas_funcionais",
                            "Value": "Térmico, Absorção de Umidade",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
                {
                    "Category": "Tops",
                    "Properties": [
                        {
                            "Property": "silhueta",
                            "Value": "Regular, Ajustada, Quadrada, Oversized, Cropped, Longa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caimento",
                            "Value": "Solto, Regular, Relaxado",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_do_decote",
                            "Value": "Gola Redonda, Decote em V, Decote U",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_das_mangas",
                            "Value": "Montada, Ombro Caído",
                            "Group": "design_features",
                        },
                        {
                            "Property": "comprimento_das_mangas",
                            "Value": "Sem Mangas, Manga Curta, Manga Longa",
                            "Group": "design_features",
                        },
                        {
                            "Property": "tipo_de_fechamento",
                            "Value": "Pulôver",
                            "Group": "design_features",
                        },
                        {
                            "Property": "estilo_da_barra",
                            "Value": "Barra Reta, Barra Curva",
                            "Group": "design_features",
                        },
                        {
                            "Property": "elementos_decorativos",
                            "Value": "Bolsos",
                            "Group": "design_features",
                        },
                        {
                            "Property": "caracteristicas_funcionais",
                            "Value": "Absorção de Umidade",
                            "Group": "design_features",
                        },
                        {
                            "Property": "Genero",
                            "Value": "female",
                            "Group": "sales_support",
                        },
                        {
                            "Property": "Faixa etária",
                            "Value": "adulto",
                            "Group": "sales_support",
                        },
                    ],
                },
            ],
            "negatives": [],
            "explanation": "1. **Step-by-step reasoning**: The query was analyzed to identify categories and properties that align with the concept of comfortable clothing for staying at home, specifically for adult females. Categories like Calças, Cardigan, Camisetas, Shorts, Suéter, and Tops were considered due to their relevance to comfort and casual wear.\n   \n2. **Criteria used**: The selection focused on properties that enhance comfort, such as loose fits, elastic waistbands, and soft materials. The gender and age group were specified as female and adult, respectively.\n   \n3. **Comparison with alternatives**: Categories like Mocassim, Rasteiras, and Sapatilhas were excluded as they are footwear and the query focused on clothing. Properties related to formal or structured clothing were also excluded.\n   \n4. **Relationships between properties**: Properties like 'caimento', 'estilo_da_cintura', and 'tipo_de_fechamento' interact to provide a comfortable fit, while 'silhueta' and 'comprimento' contribute to the overall comfort and style.\n   \n5. **Impact of each property**: 'Caimento' and 'silhueta' ensure the clothing is not restrictive, 'tipo_de_fechamento' like elastic or pullover enhances ease of wear, and 'elementos_decorativos' like pockets add functionality.\n   \n6. **Confidence level**: The confidence level is high as the properties selected are directly aligned with the user's request for comfortable, casual clothing for home use.",
        }
    ]
}
