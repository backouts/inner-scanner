from __future__ import annotations
import requests
from typing import Optional, Dict, Any

class HttpClient:
    def __init__(
        self,
        *,
        base_headers: Optional[Dict[str, str]] = None,
        timeout: int = 5,
        verify_ssl: bool = False,
        proxies: Optional[Dict[str, str]] = None,
    ):
        self.session = requests.Session()
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        if base_headers:
            self.session.headers.update(base_headers)

        if proxies:
            self.session.proxies.update(proxies)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.session.get(
            url,
            timeout=kwargs.get("timeout", self.timeout),
            verify=kwargs.get("verify", self.verify_ssl),
            allow_redirects=kwargs.get("allow_redirects", False),
        )

    def post(self, url: str, **kwargs) -> requests.Response:
        return self.session.post(
            url,
            timeout=kwargs.get("timeout", self.timeout),
            verify=kwargs.get("verify", self.verify_ssl),
        )
