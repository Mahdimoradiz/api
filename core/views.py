from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])  # مشخص می‌کند که این API فقط درخواست‌های GET را می‌پذیرد
def test_api(request):
    return Response({"this test"})