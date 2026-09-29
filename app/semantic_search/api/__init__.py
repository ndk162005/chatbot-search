from app.api.r_upload import router as upload_router
from app.api.r_search import router as search_router
from app.api.r_docs import router as docs_router

__all__ = ["upload_router", "search_router", "docs_router"]
