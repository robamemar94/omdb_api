def get_query_params(query_string):
    if not query_string:
        return {}
    return {
        key: value
        for key, value in (
            param.split('=')
            for param in query_string.split('&')
            if '=' in param
        )
    }


def extract_query_params(query_params):
    """
    Extract and convert limit, page, order_by,
    and filters from query parameters.
    """
    limit = int(query_params.get('limit', 10))
    page = int(query_params.get('page', 1))
    order_by = query_params.get('order_by', 'title')
    filters = {
        key: value
        for key, value in query_params.items()
        if key not in ['limit', 'page', 'order_by']
    }
    return limit, page, order_by, filters
