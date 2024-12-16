import subprocess
import sys
import types
import os
import pandas as pd
import json
import importlib
from sql_agent.sql_function import fetch_postgres_data
from globals import user_tokens


def install_package(package_name: str):
    """
    Install a Python package using pip.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return f"Package '{package_name}' installed successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to install package '{package_name}': {str(e)}"

##### AQUI que vamos passar para o python de cada cliente, queintegraçoes, funcoes, dados ou modulos:
# Global dictionary to hold environments for different clients

clients_environments = {}
def prepare_environment(client, functions_with_modules,sid, default_params=None):
    """
    Prepara e retorna o dicionário de ambiente para um cliente específico com funções e
    outros objetos que devem estar disponíveis no código executado dinamicamente.

    :param client: O identificador do cliente (ex.: string ou número).
    :param functions_with_modules: Lista de objetos contendo 'module' e 'function'.
    :param default_params: Dicionário de parâmetros padrão que serão passados a cada função.
    :return: O dicionário atualizado do ambiente do cliente.
    """

    if client not in clients_environments:
        # Inicializa um dicionário vazio para o cliente se não existir
        clients_environments[client] = {}

    # Função wrapper para adicionar parâmetros automaticamente
    def function_wrapper(func, params):
        # Função que será chamada no lugar da original
        def wrapped_function(*args, **kwargs):
            # Adiciona os parâmetros adicionais antes de chamar a função original
            if params:
                kwargs.update(params)
            return func(*args, **kwargs)
        return wrapped_function

    for item in functions_with_modules:
        module_name = item.get('module')  # Pega o nome do módulo
        func_name = item.get('function')  # Pega o nome da função

        if module_name and func_name:
            try:
                # Carrega o módulo dinamicamente
                module = importlib.import_module(module_name)
                # Pega a função dentro do módulo
                func = getattr(module, func_name, None)
                if func:
                    # Envolve a função original com o wrapper para incluir parâmetros padrão
                    wrapped_func = function_wrapper(func, default_params)
                    # Armazena a função no ambiente do cliente
                    clients_environments[client][func_name] = wrapped_func
                else:
                    print(f"Função {func_name} não encontrada no módulo {module_name}")
            except ModuleNotFoundError:
                print(f"Módulo {module_name} não encontrado!")
        else:
            print(f"Dados inválidos: Módulo ou função ausente em {item}")

    # Ensure __builtins__ is in the environment
      # Add built-in functions and modules
    clients_environments[client]['__builtins__'] = __builtins__.copy()

    #Load variables and presets
    clients_environments[client]['__builtins__']['sid'] = sid  # Sid is a variable
    clients_environments[client]['sid'] = sid
    clients_environments[client]['__builtins__']['pd'] = pd
    clients_environments[client]['__builtins__']['json'] = json


    # Load functions
    ########TO be loaded from MOngo auth in the future

    
    clients_environments[client]['__builtins__']['user_tokens'] = user_tokens

    # Clone filter_products_mongo and inject 'sid' into its globals
    def inject_sid(func, sid_value):
      new_globals = func.__globals__.copy()
      new_globals['sid'] = sid_value
      cloned_func = types.FunctionType(
        func.__code__,
        new_globals,
        func.__name__,
        func.__defaults__,
        func.__closure__
      )
      return cloned_func

    # Inject 'sid' into filter_products_mongo
    
    cloned_fetch_postgres_data = inject_sid(fetch_postgres_data, sid)
    clients_environments[client]['__builtins__']['fetch_postgres_data'] = cloned_fetch_postgres_data

    ###Returning a dic so in the future execute_code can hold a dic of envs.
    return clients_environments[client]


