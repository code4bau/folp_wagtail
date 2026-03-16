import json
from facultad.models import CarreraPage

def run():
    materias_data = [
        # --- PRIMER AÑO ---
        {"type": "titulo_anio", "value": "PRIMER AÑO"},
        {"type": "subtitulo_periodo", "value": "Bimestral"},
        {"type": "materia", "value": {"codigo": "0001F", "nombre": "Introducción a la Odontología", "periodicidad": "Bimestral"}},
        {"type": "subtitulo_periodo", "value": "Anual"},
        {"type": "materia", "value": {"codigo": "0001E", "nombre": "Odontología Preventiva y Social I", "periodicidad": "Anual"}},
        {"type": "subtitulo_periodo", "value": "Primer Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00011", "nombre": "Anatomía I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00012", "nombre": "Bioquímica Estomatología I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00013", "nombre": "Biofísica I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00014", "nombre": "Biología General I", "periodicidad": "1er C."}},
        {"type": "subtitulo_periodo", "value": "Segundo Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00016", "nombre": "Anatomía II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00017", "nombre": "Histología y Embriología I", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00018", "nombre": "Biofísica II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00019", "nombre": "Biología General II", "periodicidad": "2do C."}},

        # --- SEGUNDO AÑO ---
        {"type": "titulo_anio", "value": "SEGUNDO AÑO"},
        {"type": "subtitulo_periodo", "value": "Anual"},
        {"type": "materia", "value": {"codigo": "0002E", "nombre": "Odontología Preventiva y Social II", "periodicidad": "Anual"}},
        {"type": "subtitulo_periodo", "value": "Primer Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00022", "nombre": "Histología y Embriología II", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00023", "nombre": "Microbiología y Parasitología I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00024", "nombre": "Biomateriales I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00025", "nombre": "Dimensión Psicológica de la Atención Odontológica", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00021", "nombre": "Fisiología I", "periodicidad": "1er C."}},
        {"type": "subtitulo_periodo", "value": "Segundo Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00027", "nombre": "Fisiología II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00028", "nombre": "Patología y Clínica Estomatológica I", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00029", "nombre": "Microbiología y Parasitología II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0002A", "nombre": "Bioquímica Estomatología II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0002B", "nombre": "Biomateriales II", "periodicidad": "2do C."}},

        # --- TERCER AÑO ---
        {"type": "titulo_anio", "value": "TERCER AÑO"},
        {"type": "subtitulo_periodo", "value": "Anual"},
        {"type": "materia", "value": {"codigo": "0003E", "nombre": "Odontología Preventiva y Social III", "periodicidad": "Anual"}},
        {"type": "subtitulo_periodo", "value": "Primer Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00032", "nombre": "Farmacología y Terapéutica I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00033", "nombre": "Patología y Clínica Estomatológica II", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00034", "nombre": "Diagnóstico por Imágenes I", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00035", "nombre": "Operatoria Dental I A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00036", "nombre": "Prótesis I A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00031", "nombre": "Cirugía I A/B", "periodicidad": "1er C."}},
        {"type": "subtitulo_periodo", "value": "Segundo Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00037", "nombre": "Cirugía II A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00038", "nombre": "Farmacología y Terapéutica II", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00039", "nombre": "Patología y Clínica Estomatológica III", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0003A", "nombre": "Operatoria Dental II A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0003B", "nombre": "Prótesis II A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0003C", "nombre": "Diagnóstico por Imágenes II", "periodicidad": "2do C."}},

        # --- CUARTO AÑO ---
        {"type": "titulo_anio", "value": "CUARTO AÑO"},
        {"type": "subtitulo_periodo", "value": "Anual"},
        {"type": "materia", "value": {"codigo": "0004E", "nombre": "Odontología Preventiva y Social IV", "periodicidad": "Anual"}},
        {"type": "subtitulo_periodo", "value": "Primer Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00042", "nombre": "Periodoncia I A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00043", "nombre": "Cirugía III A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00044", "nombre": "Operatoria Dental III A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00045", "nombre": "Prótesis III A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00046", "nombre": "Patología y Clínica Estomatológica IV", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00041", "nombre": "Endodoncia I A/B", "periodicidad": "1er C."}},
        {"type": "subtitulo_periodo", "value": "Segundo Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00047", "nombre": "Endodoncia II A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00048", "nombre": "Periodoncia II A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00049", "nombre": "Cirugía IV A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0004A", "nombre": "Operatoria Dental IV A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0004B", "nombre": "Prótesis IV A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0004C", "nombre": "Patología y Clínica Estomatológica V", "periodicidad": "2do C."}},

        # --- QUINTO AÑO ---
        {"type": "titulo_anio", "value": "QUINTO AÑO"},
        {"type": "subtitulo_periodo", "value": "Anual"},
        {"type": "materia", "value": {"codigo": "0005E", "nombre": "Odontología Preventiva y Social V", "periodicidad": "Anual"}},
        {"type": "subtitulo_periodo", "value": "Primer Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00051", "nombre": "Odontología Integral Niños I A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00053", "nombre": "Cirugía V A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00054", "nombre": "Odontología Legal y Forense", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00055", "nombre": "Operatoria Dental V A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00056", "nombre": "Prótesis V A/B", "periodicidad": "1er C."}},
        {"type": "materia", "value": {"codigo": "00052", "nombre": "Odontología Integral Niños II A/B", "periodicidad": "1er C."}},
        {"type": "subtitulo_periodo", "value": "Segundo Cuatrimestre"},
        {"type": "materia", "value": {"codigo": "00057", "nombre": "Odontología Integral Niños III A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00058", "nombre": "Cirugía VI A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "00059", "nombre": "Bioética", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0005A", "nombre": "Operatoria Dental VI A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0005B", "nombre": "Prótesis VI A/B", "periodicidad": "2do C."}},
        {"type": "materia", "value": {"codigo": "0005D", "nombre": "P.P.S. (Prácticas Profesionales Supervisadas)", "periodicidad": "2do C."}},
    ]

    try:
        # Buscamos la página por título (asegurate que coincida)
        page = CarreraPage.objects.get(title="Carrera Odontologia")
        
        # Convertimos la lista a JSON compatible con Wagtail StreamField
        page.plan_estudios = json.dumps(materias_data)
        
        # Guardamos los cambios y publicamos
        page.save_revision().publish()
        print(">>> MIGRACIÓN EXITOSA: Se han cargado todas las materias de 1ro a 5to año.")
        
    except CarreraPage.DoesNotExist:
        print("ERROR: No se encontró la página 'Carrera Odontologia'. Verificá el nombre en el Admin.")
    except Exception as e:
        print(f"ERROR INESPERADO: {e}")

if __name__ == "__main__":
    run()