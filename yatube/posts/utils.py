from django.conf import settings
from django.core.paginator import Paginator


def paginate(request, posts):
    paginator = Paginator(posts, settings.NUM_MSG)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
