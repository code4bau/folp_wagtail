from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from wagtail.embeds.blocks import EmbedBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.embeds import get_embed

# --- 1. SNIPPETS ---

@register_snippet
class Alerta(models.Model):
    texto = models.CharField(max_length=255)
    color_urgencia = models.BooleanField(default=False, help_text="Si está marcado, será rojo. Si no, azul.")
    mostrar = models.BooleanField(default=True)

    panels = [
        FieldPanel('texto'),
        FieldPanel('color_urgencia'),
        FieldPanel('mostrar'),
    ]

    def __str__(self):
        return self.texto


# --- 2. BLOQUES REUTILIZABLES (Deber ir antes de las clases Page) ---

class BotonPopUpBlock(blocks.StructBlock):
    texto_boton = blocks.CharBlock(required=True, label="Texto del Botón (ej: Ver Especialización)")
    titulo_ventana = blocks.CharBlock(required=True, label="Título de la ventana pop-up")
    cuerpo_ventana = blocks.RichTextBlock(label="Contenido que va adentro del pop-up")
    icono = blocks.CharBlock(required=False, help_text="Ej: fa-graduation-cap", label="Icono FontAwesome")

    class Meta:
        icon = "doc-full"
        label = "Botón con Ventana Emergente"


class MateriaBlock(blocks.StructBlock):
    codigo = blocks.CharBlock(required=False, max_length=10, label="Código")
    nombre = blocks.CharBlock(required=True, label="Nombre de la materia")
    periodicidad = blocks.CharBlock(required=False, label="Periodicidad (Ej: 1er C.)")

    class Meta:
        icon = "form"
        label = "Materia"


# --- 3. PÁGINAS ---

class NoticiaPage(Page):
    fecha = models.DateField("Fecha de publicación")
    imagen = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    resumen = models.CharField(max_length=250)
    cuerpo = RichTextField(blank=True)


    prioridad = models.IntegerField(default=10)
    ancho = models.CharField(
        max_length=20, 
        choices=[('col-md-4', 'Chica'), ('col-md-8', 'Mediana'), ('col-12', 'Grande')], 
        default='col-md-4'
    )
    
    mostrar_texto_en_home = models.BooleanField(default=True)
    convertir_en_popup = models.BooleanField(default=False)
    link_externo = models.ForeignKey('wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    link_externo = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    elementos_extra = StreamField([('p', blocks.CharBlock())], blank=True, null=True, use_json_field=True)

    video_url = models.URLField(
        blank=True, 
        null=True, 
        help_text="Pegá acá el link de YouTube (ej: https://www.youtube.com/watch?v=...) para que aparezca al final de la noticia."
    )
    @property
    def video_embed_url(self):
        if self.video_url:
            import re
            # Buscamos el ID del video en cualquier formato de link de YouTube
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", self.video_url)
            if match:
                video_id = match.group(1)
                # Retornamos el link de embed con parámetros de seguridad
                return f"https://www.youtube.com/embed/{video_id}?rel=0"
        return ""
    
    boton_accion = StreamField([
        ('boton', blocks.StructBlock([
            ('texto', blocks.CharBlock(required=True)),
            ('archivo', DocumentChooserBlock(required=False)),
            ('url_externa', blocks.URLBlock(required=False)),
            ('icono_fontawesome', blocks.CharBlock(required=False)),
            ('imagen_logo', ImageChooserBlock(required=False)),
        ]))
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('prioridad'),
        FieldPanel('ancho'),
        FieldPanel('fecha'),
        FieldPanel('imagen'),
        FieldPanel('resumen'),
        FieldPanel('video_url'),
        FieldPanel('mostrar_texto_en_home'),
        FieldPanel('convertir_en_popup'),
        FieldPanel('boton_accion'),
        FieldPanel('cuerpo'),          # Texto original recuperado
        FieldPanel('link_externo'),
    ]

class FolpHomePage(Page):
    body = StreamField([
        ('carrusel', blocks.ListBlock(
            blocks.StructBlock([
                ('titulo', blocks.CharBlock(required=True)),
                ('subtitulo', blocks.TextBlock(required=False)),
                ('imagen', ImageChooserBlock()),
                ('link', blocks.PageChooserBlock(required=False)),
            ]),
            template='facultad/blocks/hero_slider.html'
        )),
        ('accesos_rapidos', blocks.ListBlock(
            blocks.StructBlock([
                ('imagen_logo', ImageChooserBlock(required=True)),
                ('etiqueta', blocks.CharBlock()),
                ('url', blocks.URLBlock()),
            ]),
            template='facultad/blocks/accesos_rapidos.html'
        )),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['noticias'] = NoticiaPage.objects.live().order_by('prioridad', '-fecha')
        return context

    class Meta:
        verbose_name = "Página de Inicio FOLP"

class PaginaEstandar(Page):
    subtitulo = models.CharField(max_length=250, blank=True)
    imagen_principal = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    video_url = models.URLField(blank=True, null=True, help_text="Link de YouTube")
    @property
    def video_embed_url(self):
        if self.video_url:
            import re
            # Buscamos el ID del video en cualquier formato de link de YouTube
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", self.video_url)
            if match:
                video_id = match.group(1)
                # Retornamos el link de embed con parámetros de seguridad
                return f"https://www.youtube.com/embed/{video_id}?rel=0"
        return ""
    # Aplicamos la misma lógica para no romper nada
    cuerpo = RichTextField(blank=True)
    boton_accion = StreamField([
        ('boton', blocks.StructBlock([
            ('texto', blocks.CharBlock(required=False)),
            ('url_o_archivo', blocks.URLBlock(required=False)),
            ('documento', blocks.PageChooserBlock(required=False)),
            ('icono_fontawesome', blocks.CharBlock(required=False)),
            ('imagen_logo', ImageChooserBlock(required=False)),
        ]))
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitulo'),
        FieldPanel('imagen_principal'),
        FieldPanel('cuerpo'),
        FieldPanel('video_url'),
        FieldPanel('boton_accion'),
    ]

class CarreraPage(Page):
    titulo_carrera = models.CharField(max_length=255, default="Carrera Odontología")
    
    plan_estudios = StreamField([
        ('titulo_anio', blocks.CharBlock(label="Título de Año")),
        ('subtitulo_periodo', blocks.CharBlock(label="Subtítulo de Periodo")),
        ('materia', MateriaBlock(label="Materia")),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('titulo_carrera'),
        FieldPanel('plan_estudios'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['notas_destacadas'] = NoticiaPage.objects.live().order_by('-fecha')[:2]
        return context