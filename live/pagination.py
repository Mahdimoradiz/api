from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.utils.translation import gettext_lazy as _


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class with additional metadata and customizable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('page_size', self.get_page_size(self.request))
        ]))


class StreamPagination(CustomPageNumberPagination):
    """
    Specific pagination class for Streams with different default page size.
    """
    page_size = 12
    

class MessagePagination(CustomPageNumberPagination):
    """
    Specific pagination class for Messages with different default page size
    and reverse ordering.
    """
    page_size = 50
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', reversed(data)),  # Reverse for chat-like display
            ('page_size', self.get_page_size(self.request))
        ]))


class CommentPagination(CustomPageNumberPagination):
    """
    Specific pagination class for Comments.
    """
    page_size = 30 