import requests

BRAPI_BASE_URL = "https://brapi.dev/api/quote"
REQUEST_TIMEOUT = 10

def fetch_brapi_data(ticker):
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker inválido: deve ser uma string não vazia.")

    formatted_ticker = ticker.strip().upper()
    if not all(c.isalnum() or c == "." for c in formatted_ticker):
        raise ValueError(f"Ticker contém caracteres inválidos: '{ticker}'")

    url = f"{BRAPI_BASE_URL}/{formatted_ticker}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("results")
        if not results or not isinstance(results, list):
            raise ValueError("Resposta da API sem campo 'results' válido.")
        return results[0]
    except requests.HTTPError as e:
        raise RuntimeError(f"Erro HTTP {response.status_code}: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro: {e}")