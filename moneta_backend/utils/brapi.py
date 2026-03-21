import time
import requests

BRAPI_BASE_URL  = "https://brapi.dev/api/quote"
REQUEST_TIMEOUT = 10
MAX_RETRIES     = 3
RETRY_DELAY     = 0.5  # segundos

_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "DNT":             "1",
    "Connection":      "keep-alive",
}

_RETRYABLE_CODES = {429, 502, 503}

def _validate_ticker(ticker: str) -> str:
    """Valida e normaliza o ticker; levanta ValueError se inválido."""
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker inválido: deve ser uma string não vazia.")

    normalized = ticker.strip().upper()
    if not all(c.isalnum() or c == "." for c in normalized):
        raise ValueError(f"Ticker contém caracteres inválidos: '{ticker}'")

    return normalized

def _handle_http_error(ticker: str, status: int, error: Exception) -> None:
    """Converte status HTTP em exceção semântica (ou relança para retry)."""
    if status in (401, 404):
        label = "não encontrado ou sem acesso" if status == 401 else "não existe"
        raise ValueError(f"Ticker '{ticker}' {label}.")
    if status not in _RETRYABLE_CODES:
        raise RuntimeError(f"Erro na API BRAPI ({status}): {error}")

def _backoff(attempt: int) -> None:
    time.sleep(RETRY_DELAY * (attempt + 1))

def fetch_brapi_data(ticker: str) -> dict:
    normalized = _validate_ticker(ticker)
    url = f"{BRAPI_BASE_URL}/{normalized}"
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)

            # trata erros antes de raise_for_status para mensagens melhores
            if response.status_code in (401, 404):
                _handle_http_error(ticker, response.status_code, None)

            if response.status_code in _RETRYABLE_CODES:
                last_error = RuntimeError(f"HTTP {response.status_code}")
                if attempt < MAX_RETRIES - 1:
                    _backoff(attempt)
                    continue
                raise RuntimeError("Limite de requisições ou serviço indisponível. Tente novamente em breve.")

            response.raise_for_status()

            results = response.json().get("results")
            if not results or not isinstance(results, list):
                raise ValueError(f"Ticker '{ticker}' não encontrado ou resposta inválida.")

            return results[0]

        except (ValueError, RuntimeError):
            raise
        except requests.HTTPError as exc:
            _handle_http_error(ticker, exc.response.status_code, exc)
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                _backoff(attempt)
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                _backoff(attempt)
            else:
                raise RuntimeError(f"Erro ao buscar dados: {exc}") from exc

    raise RuntimeError(f"Falha permanente ao buscar ticker '{ticker}': {last_error}")