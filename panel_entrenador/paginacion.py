from rest_framework.pagination import PageNumberPagination


class PaginacionPanel(PageNumberPagination):
    """?page=2&page_size=100 — respuesta: {count, next, previous, results}."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200
