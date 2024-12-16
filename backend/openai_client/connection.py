from openai import OpenAI


class OpenAISingleton:
    _instance = None
    _api_key = None  # Armazena a chave da API associada
    client = None  # Armazena o cliente da OpenAI

    def __new__(cls, api_key: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._api_key = api_key
            cls.client = cls._create_client(api_key)
        elif cls._api_key != api_key:
            # Atualiza a chave e o cliente se a chave for diferente
            cls._api_key = api_key
            cls.client = cls._create_client(api_key)
        return cls._instance

    @staticmethod
    def _create_client(api_key: str):
        return OpenAI(api_key=api_key)

    @staticmethod
    def get_instance():
        return OpenAISingleton._instance
