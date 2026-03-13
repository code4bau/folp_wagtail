from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from wagtail.embeds.blocks import EmbedBlock  # Correcto

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
    cuerpo = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('fecha'),
        FieldPanel('imagen'),
        FieldPanel('resumen'),
        FieldPanel('cuerpo'),
    ]
    # AGREGAMOS ESTO: Un selector para elegir una página interna de destino
    link_externo = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Si elegís una página acá, el botón 'Leer más' llevará a esa página en lugar de a la noticia misma."
    )
    prioridad = models.IntegerField(default=10, help_text="1 es lo más importante (aparece primero). 10 es lo normal.")

    content_panels = Page.content_panels + [
        FieldPanel('fecha'),
        FieldPanel('imagen'),
        FieldPanel('resumen'),
        FieldPanel('cuerpo'),
        FieldPanel('link_externo'), # Nuevo panel en el Admin
        FieldPanel('prioridad'), # Agregamos este panel
    ]

    CHOICES_ANCHO = [
        ('col-md-4', 'Chica (1/3 de línea)'),
        ('col-md-8', 'Mediana (2/3 de línea)'),
        ('col-12', 'Grande (Toda la línea)'),
    ]
    
    ancho = models.CharField(
        max_length=20, 
        choices=CHOICES_ANCHO, 
        default='col-md-4',
        help_text="Elegí cuánto espacio ocupa esta noticia en la Home"
    )

    content_panels = Page.content_panels + [
        FieldPanel('prioridad'),
        FieldPanel('ancho'), # Nuevo panel
        FieldPanel('fecha'),
        FieldPanel('imagen'),
        FieldPanel('resumen'),
        FieldPanel('cuerpo'),
        FieldPanel('link_externo'),
        FieldPanel('mostrar_texto_en_home'), # Nuevo Switch
    ]

    mostrar_texto_en_home = models.BooleanField(
        default=True, 
        help_text="Si se desmarca, en la Home solo se verá la imagen (ideal para banners diseñados)."
    )

class FolpHomePage(Page):
    body = StreamField([
        ('carrusel', blocks.ListBlock(
            blocks.StructBlock([
                ('titulo', blocks.CharBlock(required=True)),
                ('subtitulo', blocks.TextBlock(required=False)),
                ('imagen', ImageChooserBlock()),
                ('link', blocks.PageChooserBlock(required=False, help_text="Elegí la noticia a la que lleva")),
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
    cuerpo = StreamField([
        ('parrafo', blocks.RichTextBlock()),
        ('imagen', ImageChooserBlock()),
        ('video', EmbedBlock(help_text="Pegá el link de YouTube")), # SIN 'blocks.'
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitulo'),
        FieldPanel('imagen_principal'),
        FieldPanel('cuerpo'),
    ]

    class Meta:
        verbose_name = "Página Estándar"