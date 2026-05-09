from contextvars import ContextVar
from typing import Optional

# Context variable to store the request ID
request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

def get_request_id() -> Optional[str]:
    return request_id_ctx_var.get()

def set_request_id(request_id: str):
    request_id_ctx_var.set(request_id)
