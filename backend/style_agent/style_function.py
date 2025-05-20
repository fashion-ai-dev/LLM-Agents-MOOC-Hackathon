import requests


API_URL = "http://147.79.110.30:8086/audience/create/"
API_PASSWORD = "flamengo2024"
HEADERS = {
    "accept": "application/json",
    "password": API_PASSWORD,
    "Content-Type": "application/json",
}

###PAssar SID para identificar cliente
def semantic_search(
    payload,
    type = "TEXT",
    audience_size = 1,
    product_size = 1,
    products_to_exclude=None):
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

# a = semantic_search("Vestidos pretos lisos")
# print(a)