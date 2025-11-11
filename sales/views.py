# sales/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def pos(request):
    return render(request, 'sales/pos.html', {'page_name': 'pos'})

def sales_history(request):
    return render(request, 'sales/history.html', {'page_name': 'sales_history'})

@require_POST
def pos_checkout(request):
    # Заглушка оформления
    return JsonResponse({'ok': True})

def search(request):
    """Заглушка поиска для маршрута /pos/search/"""
    q = request.GET.get('q', '').strip()
    # тут позже вернем реальные результаты
    return JsonResponse({
        'query': q,
        'results': [],
    })
