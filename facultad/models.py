from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet

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

# 1. Modelo para las noticias individuales
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

# 2. Modelo para la Home Page (La que se conecta con tu folp_home_page.html)
# 2. Modelo para la Home Page (La que se conecta con tu folp_home_page.html)
class FolpHomePage(Page):
    # Definimos el StreamField para que sea modular como la UNLP
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
                ('imagen_logo', ImageChooserBlock(required=True, help_text="Subí el logo (PNG o SVG preferentemente)")),
                ('etiqueta', blocks.CharBlock()),
                ('url', blocks.URLBlock()),
            ]),
            template='facultad/blocks/accesos_rapidos.html'
        )),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    # Esta función busca las noticias para mostrarlas en el HTML
    def get_context(self, request):
        context = super().get_context(request)
        context['noticias'] = NoticiaPage.objects.live().order_by('-fecha')
        return context

    class Meta:
        verbose_name = "Página de Inicio FOLP"