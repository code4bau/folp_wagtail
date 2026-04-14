# facultad/views.py
from django.shortcuts import render
from .models import CursoPage, EventoPage

def metrics_dashboard(request):
    metricas = []

    # Buscamos inscripciones en Cursos
    for curso in CursoPage.objects.live():
        # Obtenemos la cantidad de envíos del formulario de cada curso
        count = curso.get_submission_class().objects.filter(page=curso).count()
        metricas.append({
            'title': curso.title,
            'tipo': 'Curso',
            'cantidad': count
        })

    # Buscamos inscripciones en Eventos
    for evento in EventoPage.objects.live():
        count = evento.get_submission_class().objects.filter(page=evento).count()
        metricas.append({
            'title': evento.title,
            'tipo': 'Evento',
            'cantidad': count
        })

    return render(request, 'facultad/admin/metrics_dashboard.html', {
        'metricas': metricas,
    })