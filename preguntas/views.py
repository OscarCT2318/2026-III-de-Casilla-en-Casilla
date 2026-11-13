from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pregunta, Nivel
from .forms import PreguntaForm

@login_required
def lista_preguntas(request):
    preguntas = Pregunta.objects.select_related('nivel', 'creador').order_by('-fecha_creacion')
    niveles = Nivel.objects.all()
    return render(request, 'preguntas/panel/lista_preguntas.html', {
        'preguntas': preguntas,
        'niveles': niveles,
    })

@login_required
def crear_pregunta(request):
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.creador = request.user
            pregunta.save()
            return redirect('preguntas:lista_preguntas')
    else:
        form = PreguntaForm()
    return render(request, 'preguntas/panel/formulario_pregunta.html', {
        'form': form,
        'accion': 'Crear'
    })

@login_required
def editar_pregunta(request, pk):
    pregunta = get_object_or_404(Pregunta, pk=pk)
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            return redirect('preguntas:lista_preguntas')
    else:
        form = PreguntaForm(instance=pregunta)
    return render(request, 'preguntas/panel/formulario_pregunta.html', {
        'form': form,
        'object': pregunta,
    })

@login_required
def eliminar_pregunta(request, pk):
    pregunta = get_object_or_404(Pregunta, pk=pk)
    if request.method == 'POST':
        pregunta.delete()
        return redirect('preguntas:lista_preguntas')
    return render(request, 'preguntas/panel/confirmar_borrado.html', {
        'pregunta': pregunta
    })