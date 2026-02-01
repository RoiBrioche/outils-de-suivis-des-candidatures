from django import template
from urllib.parse import urlencode, parse_qs

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_without_page(context, page=1):
    """
    Generate a querystring that removes any existing 'page' parameter
    and adds the new page parameter, preserving all other query parameters.
    
    Usage: {% querystring_without_page context page_num %}
    
    This fixes the pagination bug where page parameters accumulate:
    - Before: /candidatures/?page=1&page=2&page=3
    - After:  /candidatures/?search=test&statut=ENVOYE&page=2
    """
    request = context['request']
    
    # Get current query parameters from request.GET
    query_dict = request.GET.copy()
    
    # Remove any existing page parameters
    query_dict.pop('page', None)
    
    # Add the new page parameter
    query_dict['page'] = str(page)
    
    return query_dict.urlencode()


@register.simple_tag(takes_context=True)
def build_pagination_url(context, page=1):
    """
    Build a complete pagination URL with proper querystring handling.
    
    Usage: href="?{% build_pagination_url context page_num %}"
    
    This is a convenience wrapper around querystring_without_page
    that returns the querystring ready to be used in href attributes.
    """
    return querystring_without_page(context, page)


@register.simple_tag(takes_context=True)
def querystring_with_sort(context, sort_field):
    """
    Generate a querystring that removes any existing 'sort' parameter
    and adds the new sort parameter, preserving all other query parameters.
    
    Usage: {% querystring_with_sort context 'entreprise' %}
    
    This is used for column sorting while preserving filters and pagination.
    """
    request = context['request']
    
    # Get current query parameters from request.GET
    query_dict = request.GET.copy()
    
    # Remove any existing sort parameters
    query_dict.pop('sort', None)
    
    # Add the new sort parameter
    query_dict['sort'] = sort_field
    
    return query_dict.urlencode()
