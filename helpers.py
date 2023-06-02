from .client import Client

def setup_client(host: str, email: str, password: str, verify_ssl: bool, cache_seconds: int) -> Client:
    """Create a Nginx Proxy Manager client."""
    client = Client(host, verify=verify_ssl, cache_seconds=cache_seconds)
    client.login(email, password)
    return client
