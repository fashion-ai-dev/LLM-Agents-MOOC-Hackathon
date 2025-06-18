import os
import requests
from qdrant_client import models, QdrantClient

API_URL = "http://147.79.110.30:8086/audience/create/"
API_PASSWORD = "flamengo2024"
HEADERS = {
    "accept": "application/json",
    "password": API_PASSWORD,
    "Content-Type": "application/json",
}


###PAssar SID para identificar cliente
def semantic_search(
    payload, type="TEXT", audience_size=1, product_size=1, products_to_exclude=None
):
    """
    Create a semantic audience via FashionAI’s API.

    Parameters
    ----------
    type : str
        The input_type for the API (e.g., "TEXT").
    payload : str
        The search text or other payload the API should interpret.
    audience_size : int, default 1
        Desired audience size (value field passed as {"value": audience_size}).
    product_size : int, default 1
        Desired product size (value field passed as {"value": product_size}).
    products_to_exclude : list[str], optional
        List of product IDs to exclude. Defaults to an empty list.

    Returns
    -------
    dict
        The JSON response from the API (already parsed).

    Raises
    ------
    requests.HTTPError
        If the API returns a non-200 status code.
    """
    if products_to_exclude is None:
        products_to_exclude = []

    body = {
        "customer_id": "9",
        "audience_id": "",
        "input_type": type,
        "payload": payload,
        "audienceSize": {"value": audience_size},
        "productSize": {"value": product_size},
        "products_to_exclude": products_to_exclude,
    }

    response = requests.post(API_URL, headers=HEADERS, json=body, timeout=120)
    response.raise_for_status()  # raises HTTPError for bad responses
    return response.json()


from style_input_tool import fashion_input


def embed_fashion_concept(input, sid=9, taxonomy_language="PT-BR"):
    return fashion_input(input, sid, taxonomy_language)


# a = semantic_search("Vestidos pretos lisos")
# print(a)


def create_qdrant_filter(conditions_list):
    """
    Cria um filtro Qdrant a partir de uma lista de condições.

    Args:
        conditions_list (list): Lista de dicionários com formato:
            {
                "key": string,
                "value": any,
                "rule": "must/must_not",
                "match_type": "exact/range/match_any/datetime_range/match_except/uuid_match/nested_key/geo/nested_object/values_count/full_text_match/is_empty/has_id/is_null"
            }

    Returns:
        models.Filter: Objeto Filter do Qdrant com as condições especificadas
    """
    must_conditions = []
    must_not_conditions = []

    for condition in conditions_list:
        match_type = condition.get("match_type", "exact")
        key = condition["key"]
        value = condition["value"]

        # Cria o objeto match baseado no tipo especificado
        match_obj = _create_match_object(match_type, value)

        field_condition = models.FieldCondition(key=key, match=match_obj)

        if condition["rule"] == "must":
            must_conditions.append(field_condition)
        elif condition["rule"] == "must_not":
            must_not_conditions.append(field_condition)
        else:
            raise ValueError(
                f"Regra inválida: {condition['rule']}. Use 'must' ou 'must_not'"
            )

    # Cria o filtro apenas com as listas que não estão vazias
    filter_params = {}
    if must_conditions:
        filter_params["must"] = must_conditions
    if must_not_conditions:
        filter_params["must_not"] = must_not_conditions

    return models.Filter(**filter_params)


def _create_match_object(match_type, value):
    """
    Cria o objeto match apropriado baseado no tipo especificado.
    """
    match match_type:
        case "exact":
            return models.MatchValue(value=value)

        case "range":
            # value deve ser um dict com 'gte', 'gt', 'lte', 'lt'
            return models.Range(**value)

        case "match_any":
            # value deve ser uma lista de valores
            return models.MatchAny(any=value)

        case "datetime_range":
            # value deve ser um dict com 'gte', 'gt', 'lte', 'lt' em formato datetime
            datetime_params = {}
            for key, val in value.items():
                if isinstance(val, str):
                    datetime_params[key] = datetime.fromisoformat(val)
                else:
                    datetime_params[key] = val
            return models.DatetimeRange(**datetime_params)

        case "match_except":
            # value deve ser uma lista de valores para excluir
            return models.MatchExcept(except_=value)

        case "uuid_match":
            return models.MatchValue(value=value)  # UUID é tratado como valor exato

        case "nested_key":
            # value deve ser um dict com a estrutura aninhada
            return models.NestedCondition(**value)

        case "geo":
            # value deve ser um dict com parâmetros geográficos
            if "radius" in value:
                return models.GeoRadius(**value)
            elif "polygon" in value:
                return models.GeoPolygon(**value)
            elif "bounding_box" in value:
                return models.GeoBoundingBox(**value)
            else:
                raise ValueError("Parâmetros geográficos inválidos")

        case "nested_object":
            # value deve ser um dict com a condição do objeto aninhado
            return models.NestedCondition(**value)

        case "values_count":
            # value deve ser um dict com 'gte', 'gt', 'lte', 'lt'
            return models.ValuesCount(**value)

        case "full_text_match":
            return models.MatchText(text=value)

        case "is_empty":
            return models.IsEmptyCondition()

        case "has_id":
            # value deve ser uma lista de IDs
            return models.HasIdCondition(has_id=value)

        case "is_null":
            return models.IsNullCondition()

        case _:
            raise ValueError(f"Tipo de match inválido: {match_type}")


def search_products(listadeembeddings, filtros, sid=9):
    qdrant_url = os.getenv("QDRANT_URL")
    client = QdrantClient(url=qdrant_url)

    result = client.query_points(
        collection_name="product_embeddings_text_properties",
        query=listadeembeddings,
        query_filter=create_qdrant_filter(filtros),
    )

    return result.points


def search_users(listadeembeddings, filtros, sid=9):
    pass


# chamada Qdrant para collection d products coms os embeddings e o filtro.
# models.Filter(
#     must=[
#         models.FieldCondition(
#             key="city",
#             match=models.MatchValue(value="London"),
#         ),
#         models.FieldCondition(
#             key="color",
#             match=models.MatchValue(value="red"),
#         ),
#     ]
# # )
### passar regra dos filtro do qdrant:key= ex category, MUST/MUST NOT + https://qdrant.tech/articles/vector-search-filtering/+ valores

#### Agregar filtro de customer_id ao objeot de filtro
