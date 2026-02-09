from .models import ComplianceExpediente

# ==============================================================================
# 1. EL CATÁLOGO (EL CEREBRO LEGAL)
# Contiene la configuración exacta de las 24 preguntas del reporte.
# ==============================================================================
CATALOGO_PREGUNTAS = {
    "caaue1_incluye_actividades_previas": {
        "numero": "1",
        "pregunta": "¿El expediente de contrataciones incluyó las Actividades Previas?",
        "puntos": 5,
        "condicion_error": "Se evidenció que no contiene las Actividades Previas.",
        "criterio_legal": "Artículos 6.2, 19, 20, 166.1 LCP; 2.3, 7, 32.1, 33, 111 RLCP; 31, 32 LOPA; unidad del expediente Sentencia SPA-TSJ 22-01-2002 (caso RAMÓN A. GUILLÉN); 22 LCC; 38.5.91.1.9 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue2_incluye_acta_inicio": {
        "numero": "2",
        "pregunta": "¿El expediente de contrataciones incluyó el Acta de Inicio?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene el Acta de Inicio.",
        "criterio_legal": "Artículos 19, 20, 166.3 LCP; 32.2, 107 RLCP; 31, 32 LOPA; 6 LCC; 38.5, 91.1.9 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue3_incluye_pliego_condiciones": {
        "numero": "3",
        "pregunta": "¿El expediente de contrataciones incluyó el Pliego de Condiciones?",
        "puntos": 7,
        "condicion_error": "Se evidenció que no contiene el pliego de condiciones.",
        "criterio_legal": "Artículos 19, 20, 66 LCP; 32.3 RLCP; 31, 32 LOPA; 6 LCC; 35, 38 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue4_publicacion_llamado_snc": {
        "numero": "4",
        "pregunta": "¿El expediente de contrataciones incluyó la publicación del Llamado en el portal web SNC?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene la publicación del Llamado en el portal web SNC.",
        "criterio_legal": "Artículos 19, 20, 53.4, 79, 80 LCP; 32.5, 103 RLCP; 31, 32 LOPA; 1, 6, 9 LCC; 6 LCC; 38.5, 91.1.9 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue5_publicacion_llamado_ente": {
        "numero": "5",
        "pregunta": "¿El expediente de contrataciones incluyó la publicación del llamado en el portal web del órgano u ente?",
        "puntos": 5,
        "condicion_error": "Se evidenció que no contiene la publicación del llamado en el portal web del órgano u ente.",
        "criterio_legal": "Artículos 19, 20, 79, 80 LCP; 32.5, 103, RLCP; 31, 32 LOPA; 6 LCC; 38.5, 91.1.9 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue6_incluye_registro_adquirientes": {
        "numero": "6",
        "pregunta": "¿El expediente de contrataciones incorporó el Registro de Adquirientes?",
        "puntos": 5,
        "condicion_error": "Se constató que no incorporó el Registro de Adquirientes.",
        "criterio_legal": "Artículos 19, 20, 65 LCP; 32.13 RLCP; 31, 32 LOPA; 6 LCC; 38.5, 91.1.9 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue7_incluye_solicitudes_modificaciones": {
        "numero": "7",
        "pregunta": "¿El expediente de contrataciones incluyó solicitudes de modificaciones y aclaratorias?",
        "puntos": 2,
        "condicion_error": "Se evidenció que no contiene las Solicitudes de Modificaciones y Aclaratorias.",
        "criterio_legal": "Artículos 19, 20, 68, 69 LCP; 32.6 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue8_incluye_acta_recepcion_sobres": {
        "numero": "8",
        "pregunta": "¿El expediente de contrataciones contempló el acta de recepción de sobres contentivo de la manifestación de voluntad de participar, documentos de calificación y ofertas?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene el Acta de Recepción de sobres contentivo de la Manifestación de voluntad de participar, documentos de calificación y Ofertas.",
        "criterio_legal": "Artículos 19, 20, 78.1, 91, 92 LCP; 32.7, 96 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue9_incluye_acta_apertura_sobres": {
        "numero": "9",
        "pregunta": "¿El expediente de contrataciones incluyó el acta de apertura de sobres contentivo de la manifestación de voluntad de participar, recaudos legales-financieros y ofertas?",
        "puntos": 5,
        "condicion_error": "Se evidenció que no contiene el Acta de Apertura de sobres contentivo de la Manifestación de voluntad de participar, recaudos legales-financieros y Ofertas.",
        "criterio_legal": "Artículos 19, 20, 78.1, 93 LCP; 32.13 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue10_incluye_ofertas": {
        "numero": "10",
        "pregunta": "¿El expediente de contrataciones incluyó las ofertas?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene las Ofertas.",
        "criterio_legal": "Artículos 19, 20 LCP; 32.8 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue11_incluye_garantias_sostenimiento": {
        "numero": "11",
        "pregunta": "¿El expediente de contrataciones agregó las Garantías de sostenimiento de la oferta de los oferentes?",
        "puntos": 5,
        "condicion_error": "Se evidenció que no contiene las Garantías de sostenimiento de la oferta de los oferentes.",
        "criterio_legal": "Artículos 19, 20, 63, 64, LCP; 32.13 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue12_incluye_certificado_rnc": {
        "numero": "12",
        "pregunta": "¿El expediente de contrataciones incluyó el certificado de inscripción ante el Registro Nacional de Contratistas de los oferentes?",
        "puntos": 3,
        "condicion_error": "Se constató que no contiene el certificado de inscripción ante el Registro Nacional de Contratistas de los oferentes.",
        "criterio_legal": "Artículos 19, 20, 42.1, 47 LCP; 32.13, 85 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue13_incluye_certificado_snc": {
        "numero": "13",
        "pregunta": "¿El expediente de contrataciones agregó certificado de la calificación de los oferentes del SNC?",
        "puntos": 3,
        "condicion_error": "Se evidenció que no contiene el certificado de la calificación de los oferentes del SNC.",
        "criterio_legal": "Artículos 19, 20, 42.2 LCP; 32.13 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    " caaue14_incluye_solvencias": {
        "numero": "14",
        "pregunta": "¿El expediente de contrataciones incorporó las Solvencias requeridas (banavih, laboral, ivss, inces)?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene las Solvencias requeridas (banavih, laboral, ivss, inces).",
        "criterio_legal": "Artículos 19, 20 LCP; 32.13, 127 RLCP; 31, 32 LOPA; Resolución No. 8.100 del 29-11-2012 G.O. #40.064 del 04-12-2012, Ministerio del Poder Popular para el Trabajo y Seguridad Social; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue15_incluye_informe_recomendacion": {
        "numero": "15",
        "pregunta": "¿El expediente de contrataciones incluyó el informe de recomendación?",
        "puntos": 7,
        "condicion_error": "Se evidenció que no contiene el Informe de Recomendación.",
        "criterio_legal": "Artículos 19, 20, 95 LCP; 22, 32.9 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue16_incluye_adjudicacion": {
        "numero": "16",
        "pregunta": "¿El expediente de contrataciones incluyó la adjudicación o su equivalente?",
        "puntos": 5,
        "condicion_error": "Se constató que no contiene la adjudicación o su equivalente.",
        "criterio_legal": "Artículos 19, 20 LCP; 32.10 RLCP; 31, 32 LOPA; 1,6 LCC; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue17_incluye_notificacion": {
        "numero": "17",
        "pregunta": "¿El expediente de contrataciones incluyó la notificación de interesados?",
        "puntos": 4,
        "condicion_error": "Se evidenció que no contiene la Notificación de interesados.",
        "criterio_legal": "Artículos 19, 20 LCP; 32.11, 126 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue18_incluye_garantias_contratacion": {
        "numero": "18",
        "pregunta": "¿El expediente de contrataciones agregó las garantías de la contratación?",
        "puntos": 3,
        "condicion_error": "Se constató que no contiene las Garantías de la Contratación.",
        "criterio_legal": "Artículos 19, 20 LCP; 32.13, 127 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue19_incluye_contrato_u_orden": {
        "numero": "19",
        "pregunta": "¿El expediente de contrataciones incluyó el Contrato, orden de compra u orden de servicio?",
        "puntos": 5,
        "condicion_error": "Se evidenció que no contiene el Contrato, orden de compra u orden de servicio.",
        "criterio_legal": "Artículos 6.32, 19, 20 LCP; 32.12, 132 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue20_incluye_resp_social": {
        "numero": "20",
        "pregunta": "¿El expediente incluyó el cumplimiento del compromiso de responsabilidad social?",
        "puntos": 2,
        "condicion_error": "Se constató que no contiene el cumplimiento del compromiso de responsabilidad social.",
        "criterio_legal": "Artículos 6.24, 19, 20 LCP; 32.13 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (2) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue21_identificacion_nomenclatura": {
        "numero": "21",
        "pregunta": "¿El expediente fue debidamente identificado con la nomenclatura del proceso, nombre del contratante y contratista, y objeto, conforme a lo establecido en el Art. 34, numeral 1 de las Normas SUNAI?",
        "puntos": 3,
        "condicion_error": "Se evidenció que el expediente no fue debidamente identificado con la nomenclatura del proceso, nombre del contratante y contratista, y objeto, conforme a lo establecido en el Art. 34, numeral 1 de las Normas SUNAI.",
        "criterio_legal": "Artículos 32 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (1) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue22_expediente_foliado": {
        "numero": "22",
        "pregunta": "¿Se verificó que todos los documentos del expediente se encontraban debidamente foliados en estricto orden cronológico, conforme a su fecha de incorporación, cumpliendo con lo establecido en el Art. 34, numeral 4 de las Normas SUNAI?",
        "puntos": 2,
        "condicion_error": "Se constató que no se verificó que todos los documentos del expediente se encontraban debidamente foliados en estricto orden cronológico, conforme a su fecha de incorporación, cumpliendo con lo establecido en el Art. 34, numeral 4 de las Normas SUNAI.",
        "criterio_legal": "Artículos 32 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (4) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue23_identificacion_tomos": {
        "numero": "23",
        "pregunta": "¿Se constató que el expediente, en caso de estar conformado por múltiples piezas o tomos, cada unidad documental se encontraba debidamente identificada y vinculada al proceso principal, conforme al Art. 34, numeral 4 de las Normas SUNAI?",
        "puntos": 2,
        "condicion_error": "Se evidenció que no se constató que el expediente, en caso de estar conformado por múltiples piezas o tomos, cada unidad documental se encontraba debidamente identificada y vinculada al proceso principal, conforme al Art. 34, numeral 4 de las Normas SUNAI.",
        "criterio_legal": "Artículos 32 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (4) NORMAS DE CONTROL INTERNO SUNAI.",
    },
    "caaue24_archivo_custodia": {
        "numero": "24",
        "pregunta": "¿Se verificó que el archivo y custodia del expediente se realizó en la unidad administrativa financiera del ente contratante, (o en la unidad que corresponda según la normativa interna) cumpliendo con lo dispuesto en el Art. 34, numeral 5 de la normativa aplicable",
        "puntos": 2,
        "condicion_error": "Se constató que no se verificó que el archivo y custodia del expediente se realizó en la unidad administrativa financiera del ente contratante, (o en la unidad que corresponda según la normativa interna) cumpliendo con lo dispuesto en el Art. 34, numeral 5 de la normativa aplicable.",
        "criterio_legal": "Artículos 32 RLCP; 31, 32 LOPA; 6 LCC; 38.5.91.1.9.29 LOCGR; 34 (5) NORMAS DE CONTROL INTERNO SUNAI.",
    },
}


# ==============================================================================
# 2. LA CALCULADORA (EL MOTOR)
# Esta función toma un reporte guardado en BD, revisa qué respondió el usuario
# ("SI", "NO", "NA") y genera la lista limpia para el PDF.
# ==============================================================================
def generar_data_para_pdf(reporte: ComplianceExpediente):
    """
    Recibe un objeto ComplianceExpediente (con datos SI/NO/NA)
    y devuelve una lista de diccionarios lista para el HTML.
    """
    lista_detalles = []
    total_puntos = 0
    maximos_posibles = 0

    # Recorremos nuestro catálogo pregunta por pregunta
    for campo_bd, info_catalogo in CATALOGO_PREGUNTAS.items():
        # 1. Obtenemos qué respondió el usuario en este campo (SI, NO, NA)
        respuesta_usuario = getattr(reporte, campo_bd, "NA")

        # 2. Preparamos el item para la tabla
        item = {
            "numero": info_catalogo["numero"],
            "pregunta": info_catalogo["pregunta"],
            "cumple": respuesta_usuario,  # Esto será "SI", "NO" o "NA"
            "condicion": "",
            "criterio": "",
        }

        # 3. Aplicamos la Lógica del Semáforo
        if respuesta_usuario == "SI":
            # Si CUMPLE: Sumamos puntos y no ponemos regaños
            total_puntos += info_catalogo["puntos"]
            maximos_posibles += info_catalogo["puntos"]
            item["condicion"] = ""
            item["criterio"] = ""

        elif respuesta_usuario == "NO":
            # Si NO CUMPLE: No sumamos puntos, pero SÍ ponemos el regaño legal
            maximos_posibles += info_catalogo[
                "puntos"
            ]  # El punto era posible, pero lo perdió
            item["condicion"] = info_catalogo["condicion_error"]
            item["criterio"] = info_catalogo["criterio_legal"]

        elif respuesta_usuario == "NA":
            # Si NO APLICA: Es neutral.
            item["condicion"] = "No aplica para este expediente."
            item["criterio"] = ""

        lista_detalles.append(item)

    return {
        "detalles": lista_detalles,
        "total_puntos": total_puntos,
        "maximos_posibles": maximos_posibles,
        "reporte": reporte,  # Pasamos el objeto original para sacar nombre, fecha, etc.
    }
