from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, ObjectList, PageChooserPanel, TabbedInterface, FieldRowPanel, TabbedInterface
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from wagtail.documents.blocks import DocumentChooserBlock
from django import forms
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalManyToManyField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractForm, AbstractFormField, DjangoJSONEncoder
from wagtail.contrib.forms.forms import WagtailAdminFormPageForm
from wagtail.contrib.forms.panels import FormSubmissionsPanel
import json

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

@register_snippet
class CategoriaCurso(models.Model):
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)

    panels = [FieldPanel('nombre'), FieldPanel('slug')]

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de Curso"
        verbose_name_plural = "Categorías de Cursos"

class CursoFormField(AbstractFormField):
    page = ParentalKey('CursoPage', on_delete=models.CASCADE, related_name='form_fields')

    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=list(AbstractFormField.field_type.field.choices) + [('file', 'File')]
    )

class CursoPage(AbstractEmailForm):
    # --- Datos de Cabecera (Izquierda) ---
    imagen_afiche = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, null=True, related_name='+'
    )
    descripcion_corta = models.TextField(blank=True, help_text="Se muestra en la card del índice")

    base_form_class = WagtailAdminFormPageForm

    # --- Datos de Cabecera (Derecha - Info Rápida con Íconos) ---
    categorias = ParentalManyToManyField('facultad.CategoriaCurso', blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)
    duracion = models.CharField(max_length=255, blank=True, help_text="Ej: 18 Sesiones")
    horario = models.CharField(max_length=255, blank=True, help_text="Ej: De 9:00 a 16:00hs")

    # --- Sección "Más Información" (Cuerpo) ---
    requisitos = RichTextField(blank=True)
    modalidad_detalle = RichTextField(blank=True)
    forma_pago = RichTextField(blank=True)
    cupo_disponible = models.CharField(max_length=255, blank=True)
    docentes = RichTextField(blank=True)

    # --- Sidebar de Datos (Derecha con Íconos) ---
    modalidad_resumen = models.CharField(max_length=255, blank=True, help_text="Ej: Teórico con práctica clínica")
    link_programa = models.URLField(blank=True, help_text="URL para descargar el PDF del programa")
    arancel_socios = models.CharField(max_length=255, blank=True)
    arancel_no_socios = models.CharField(max_length=255, blank=True)
    matricula = models.CharField(max_length=255, blank=True)

    # Organización de los paneles en el Admin (para que no sea una lista eterna)
    content_panels = [
        FieldPanel('title'), # Siempre es bueno tener el título a mano
        MultiFieldPanel([
            FieldPanel('imagen_afiche'),
            FieldPanel('descripcion_corta'),
            FieldPanel('categorias', widget=forms.CheckboxSelectMultiple),
        ], heading="Información Visual y Categorías"),

        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('fecha_inicio'),
                FieldPanel('fecha_finalizacion'),
            ]),
            FieldPanel('duracion'),
            FieldPanel('horario'),
        ], heading="Datos de Cabecera (Info Rápida)"),

        MultiFieldPanel([
            FieldPanel('requisitos'),
            FieldPanel('modalidad_detalle'),
            FieldPanel('forma_pago'),
            FieldPanel('cupo_disponible'),
            FieldPanel('docentes'),
        ], heading="Cuerpo: Más Información (RichText)"),

        MultiFieldPanel([
            FieldPanel('modalidad_resumen'),
            FieldPanel('link_programa'),
            FieldPanel('arancel_socios'),
            FieldPanel('arancel_no_socios'),
            FieldPanel('matricula'),
        ], heading="Sidebar de Datos Técnicos"),
    ]

    # 2. Paneles del Formulario (Lo que se verá en la pestaña 'Formulario')
    form_panels = [
        FormSubmissionsPanel(), # Esto agrega el botón de "Ver envíos"
        InlinePanel('form_fields', label="Campos del Formulario"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Configuración del Correo Electrónico"),
    ]

    # 3. Organización de las Pestañas (Tabbed Interface)
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Contenido'),
        ObjectList(form_panels, heading='Formulario'), # Usamos nuestro nuevo form_panels
        ObjectList(AbstractEmailForm.promote_panels, heading='Promoción'),
        ObjectList(AbstractEmailForm.settings_panels, heading='Configuración'),
    ])

    def get_template(self, request):
        return 'facultad/curso_page.html'

    def process_form_submission(self, form):
        submission = super().process_form_submission(form)
        # El envío de email se dispara automáticamente gracias a super() 
        # siempre y cuando hayas llenado los campos en la pestaña "Formulario"
        return submission
    
# 3. Índice de Cursos (La que tiene el buscador y filtros)
class CursoIndexPage(Page):
    intro = models.TextField(blank=True)

    def get_context(self, request):
        context = super().get_context(request)
        # Obtenemos todos los cursos hijos
        cursos = CursoPage.objects.live().public().child_of(self).order_by('-first_published_at')
        
        # Filtro por Categoría
        cat_slug = request.GET.get('categoria')
        if cat_slug:
            cursos = cursos.filter(categorias__slug=cat_slug)
            
        # Filtro por Buscador
       # Dentro del método get_context de CursoIndexPage
        search_query = request.GET.get('query')
        query_string = request.GET.get('query', None)
        if search_query:
    # Quitamos espacios extra al principio y al final
         search_query = search_query.strip()
    # Buscamos en el título O en la descripción corta
        if query_string:
         cursos = cursos.filter(
         models.Q(title__icontains=query_string) | 
         models.Q(descripcion_corta__icontains=query_string)
    ).distinct()

        context['cursos'] = cursos
        context['categorias'] = CategoriaCurso.objects.all()
        return context

class EventosIndexPage(Page):
    # Esta es la página de tu foto (image_d856ee.png)
    subpage_types = ['facultad.CursoPage', 'facultad.EventosIndexPage', 'facultad.EventoPage']
    
    # Podés agregar una imagen de cabecera si querés
    banner_image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('banner_image'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Obtenemos las páginas hijas (Jornadas, Congresos, etc.)
        context['eventos'] = self.get_children().live().specific()
        return context

    class Meta:
        verbose_name = "Índice de Eventos Institucionales"

class EventoFormField(AbstractFormField):
    page = ParentalKey('EventoPage', on_delete=models.CASCADE, related_name='form_fields')

class EventoPage(AbstractEmailForm):
    # Campos específicos para Congresos/Jornadas
    imagen_afiche = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, null=True, related_name='+'
    )
    descripcion_corta = models.TextField(blank=True)
    
    # Datos de cabecera (simplificados)
    fecha_evento = models.DateField(null=True, blank=True)
    lugar = models.CharField(max_length=255, blank=True, help_text="Ej: Aula Magna")
    
    # Cuerpo de información
    informacion_general = RichTextField(blank=True)
    disertantes = RichTextField(blank=True) # Campo nuevo que no tienen los cursos
    arancel = models.CharField(max_length=255, blank=True)

    # Configuración de los paneles (solo lo que necesitás)
    content_panels = [
        FieldPanel('title'),
        FieldPanel('imagen_afiche'),
        FieldPanel('descripcion_corta'),
        MultiFieldPanel([
            FieldPanel('fecha_evento'),
            FieldPanel('lugar'),
            FieldPanel('arancel'),
        ], heading="Datos del Evento"),
        FieldPanel('informacion_general'),
        FieldPanel('disertantes'),
        InlinePanel('form_fields', label="Campos del Formulario de Inscripción"),
    ]

    # ... No te olvides de los form_panels que hicimos antes para el mail ...
    form_panels = [
        FormSubmissionsPanel(),
        InlinePanel('form_fields', label="Campos del Formulario"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Configuración del Correo Electrónico"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Contenido'),
        ObjectList(form_panels, heading='Formulario'),
        ObjectList(AbstractEmailForm.promote_panels, heading='Promoción'),
        ObjectList(AbstractEmailForm.settings_panels, heading='Configuración'),
    ])

    def get_template(self, request):
        # Podés usar el mismo HTML de cursos o uno nuevo 'facultad/evento_page.html'
        return 'facultad/curso_page.html'

# --- 2. BLOQUES REUTILIZABLES (DEBEN IR ARRIBA DE LAS CLASES PAGE) ---

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
    
    # El primer PDF (Parte 1 o Único)
    documento = DocumentChooserBlock(required=False, label="PDF Parte 1 / Único")
    
    # El segundo PDF (Parte 2 - Opcional)
    documento_2 = DocumentChooserBlock(required=False, label="PDF Parte 2 (Solo si tiene /)")

    class Meta:
        icon = "form"
        label = "Materia"

class BotonTecnicaturaBlock(blocks.StructBlock):
    texto = blocks.CharBlock(required=True, label="Texto del botón")
    pagina = blocks.PageChooserBlock(required=False, label="Vincular a una Página")
    documento = DocumentChooserBlock(required=False, label="Vincular a un PDF")
    color = blocks.ChoiceBlock(choices=[
        ('btn-dark-green', 'Verde Oscuro'),
        ('btn-light-green', 'Verde Claro'),
        ('btn-gray', 'Gris'),
    ], default='btn-dark-green')

class TecnicaturaBloque(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True)
    imagen = ImageChooserBlock(required=True)
    botones = blocks.ListBlock(BotonTecnicaturaBlock(), label="Botones de la tarjeta")

    class Meta:
        template = "facultad/blocks/tecnicatura_block.html"
        icon = "doc-full"


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
    link_externo = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    video_url = models.URLField(blank=True, null=True, help_text="Link de YouTube")

    @property
    def video_embed_url(self):
        if self.video_url:
            import re
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", self.video_url)
            if match:
                video_id = match.group(1)
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
        FieldPanel('cuerpo'),
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
        noticias = list(NoticiaPage.objects.live().child_of(self))        
        todo_el_contenido = sorted(noticias, key=lambda x: x.prioridad)
        context['contenidos'] = todo_el_contenido
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
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", self.video_url)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/embed/{video_id}?rel=0"
        return ""

    cuerpo_tecnicaturas = StreamField([
        ('tecnicatura', TecnicaturaBloque()),
    ], use_json_field=True, blank=True)
    
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
        FieldPanel('cuerpo_tecnicaturas'), # Agregado aquí para que se vea en el admin
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

class BlogPageRelatedNews(Orderable):
    page = ParentalKey('NoticiasBlogPage', related_name='related_news')
    noticia = models.ForeignKey(
        'NoticiaPage', 
        on_delete=models.CASCADE, 
        related_name='+'
    )
    panels = [PageChooserPanel('noticia')]

class NoticiasBlogPage(Page):
    subtitulo = models.CharField(max_length=250, blank=True)
    color_seccion = models.CharField(
        max_length=20, 
        choices=[('verde', 'Verde'), ('azul', 'Azul')], 
        default='verde'
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('subtitulo'),
        FieldPanel('color_seccion'),
        InlinePanel('related_news', label="Migrar noticias de otras secciones"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        hijas = list(self.get_children().live().specific())
        migradas = [rel.noticia for rel in self.related_news.all()]
        todas = sorted(hijas + migradas, key=lambda x: x.fecha, reverse=True)
        context['entradas'] = todas
        return context