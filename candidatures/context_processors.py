from urllib.parse import urlencode

def pagination_context(request):
    """
    Add pagination context variables to all templates.
    
    Provides a clean querystring without the 'page' parameter
    to fix pagination bugs where page parameters accumulate.
    """
    # Get current query parameters and remove 'page'
    query_params = request.GET.copy()
    query_params.pop('page', None)
    
    # Create clean querystring for pagination links
    clean_querystring = query_params.urlencode()
    
    return {
        'clean_querystring': clean_querystring,
    }
