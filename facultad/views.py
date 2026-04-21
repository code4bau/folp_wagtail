# facultad/views.py
from django.shortcuts import render
from .models import CursoPage, EventoPage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import NoticiaClick
from wagtail.models import Page


def metrics_dashboard(request):
    metricas = []

    # 1. Tu lógica actual de Inscripciones (Cursos y Eventos)
    for curso in CursoPage.objects.live():
        count = curso.get_submission_class().objects.filter(page=curso).count()
        metricas.append({
            'title': curso.title,
            'tipo': 'Curso',
            'cantidad': count,
        })

    return render(request, 'facultad/admin/metrics_dashboard.html', {
        'metricas': metricas,
    })


@require_POST
def registrar_click_noticia(request, page_id):
    try:
        noticia = Page.objects.get(id=page_id)
        NoticiaClick.objects.create(noticia=noticia)
        return JsonResponse({'status': 'ok'})
    except Page.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)