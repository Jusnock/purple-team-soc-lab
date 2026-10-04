import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_proposal_docx(output_path, diagram_img_path):
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Styles & Fonts
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Palette
    COLOR_PRIMARY = RGBColor(0x1B, 0x36, 0x5D)    # Navy Blue
    COLOR_SECONDARY = RGBColor(0x8B, 0x00, 0x00)  # Crimson / Red Team
    COLOR_BLUE_TEAM = RGBColor(0x00, 0x5C, 0x8A)  # Steel Blue
    COLOR_PURPLE = RGBColor(0x5E, 0x24, 0x8C)     # Purple Team

    # Header / Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_pre = title_p.add_run("PROPUESTA DE PROYECTO TÉCNICO & PORTFOLIO DE CIBERSEGURIDAD\n")
    run_pre.font.size = Pt(10.5)
    run_pre.font.bold = True
    run_pre.font.color.rgb = COLOR_PURPLE

    run_title = title_p.add_run("SOC & Purple Team Enterprise Simulation Lab")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_before = Pt(2)
    subtitle_p.paragraph_format.space_after = Pt(12)
    run_sub = subtitle_p.add_run("Adversary Emulation (Red), Detection Engineering & SIEM Analytics (Blue) con Enfoque de Empleabilidad")
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # Callout Box: Objetivo General
    tbl_callout = doc.add_table(rows=1, cols=1)
    tbl_callout.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = tbl_callout.cell(0, 0)
    set_cell_background(c_cell, "F0F4F8")
    set_cell_margins(c_cell, top=120, bottom=120, left=180, right=180)
    cp = c_cell.paragraphs[0]
    cp.paragraph_format.space_after = Pt(0)
    cr1 = cp.add_run("🎯 Objetivo Principal: ")
    cr1.bold = True
    cr1.font.color.rgb = COLOR_PRIMARY
    cr2 = cp.add_run("Construir un laboratorio práctico, modular y reproducible que combine simulación de adversarios (Red Team) con telemetría avanzada, correlación en SIEM y reglas de detección (Blue Team). El proyecto culminará con un portafolio documentado (write-ups, reglas Sigma, matrices MITRE ATT&CK) diseñado para publicar en LinkedIn y demostrar competencias profesionales reales ante reclutadores y líderes de ciberseguridad.")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_custom_heading(text, level=1, color=COLOR_PRIMARY):
        p = doc.add_paragraph()
        p.paragraph_format.keep_with_next = True
        if level == 1:
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(text)
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = color
        elif level == 2:
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text)
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = COLOR_PURPLE
        return p

    # --- SECCIÓN 1: Fundamento Purple Team ---
    add_custom_heading("1. Fundamento del Enfoque Purple Team", 1, COLOR_PURPLE)
    p = doc.add_paragraph()
    p.add_run("En la industria actual, los analistas de SOC más demandados son aquellos que ")
    p.add_run("comprenden la mecánica interna del atacante").bold = True
    p.add_run(" (procesos, llamadas a la API de Windows/Linux, telemetría y artefactos) para diseñar ")
    p.add_run("detecciones precisas con bajo índice de falsos positivos").bold = True
    p.add_run(".\n\nEste laboratorio adopta el ciclo continuo de Purple Teaming:")

    cycle_items = [
        ("1. Emular TTP Ofensivo (Red Team): ", "Ejecutar de forma controlada y segura una técnica real de MITRE ATT&CK (ej. fuerza bruta SSH/RDP, volcado de LSASS, persistencia vía tareas programadas)."),
        ("2. Inspeccionar Telemetría (Blue Team): ", "Verificar si la actividad generó logs en Sysmon, Windows Security Logs, Auditd o NIDS."),
        ("3. Identificar Brechas de Visibilidad: ", "Evaluar si el SIEM/EDR generó una alerta o si el ataque pasó desapercibido."),
        ("4. Desarrollar Detección (Detection-as-Code): ", "Crear una regla Sigma, convertirla a la consulta del SIEM (Wazuh/Elastic) y configurar la severidad y respuesta adecuada."),
        ("5. Re-evaluar y Documentar: ", "Volver a ejecutar el test para confirmar la detección y documentar el caso de uso para el portafolio.")
    ]
    for bold_text, normal_text in cycle_items:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r1 = bp.add_run(bold_text)
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        bp.add_run(normal_text)

    # --- SECCIÓN 2: Diagrama de Arquitectura de Red ---
    add_custom_heading("2. Diagrama de Arquitectura y Topología de Red", 1, COLOR_PRIMARY)
    p_diag = doc.add_paragraph()
    p_diag.add_run("A continuación se presenta la arquitectura del laboratorio completamente aislada en VirtualBox utilizando el direccionamiento privado ")
    p_diag.add_run("192.168.56.0/24 (Host-Only vboxnet0)").bold = True
    p_diag.add_run(" con doble interfaz NAT para acceso seguro a Internet:")

    # Insert Image
    if os.path.exists(diagram_img_path):
        doc.add_picture(diagram_img_path, width=Inches(6.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figura 1: Topología de Red y Flujo de Telemetría del Laboratorio Purple Team.")
        rc.font.size = Pt(8.5)
        rc.font.italic = True
        rc.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Tabla de Nodos
    tbl_arch = doc.add_table(rows=5, cols=4)
    tbl_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Segmento", "Máquina / IP", "Tecnología Principal", "Función en el Lab"]
    for i, h in enumerate(headers):
        cell = tbl_arch.cell(0, i)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        hp = cell.paragraphs[0]
        hp.paragraph_format.space_after = Pt(0)
        hr = hp.add_run(h)
        hr.bold = True
        hr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        hr.font.size = Pt(9)

    arch_data = [
        ("Red Team\n(Atacante)", "Kali Linux\n192.168.56.20", "Atomic Red Team, Hydra, NetExec, Nmap", "Ejecución de ataques, Password Spraying, fuerza bruta y emulación de TTPs."),
        ("Victim Windows\n(Endpoint)", "Windows 11 Ent.\n192.168.56.10", "Sysmon (SwiftOnSecurity config), Agente Wazuh", "Host víctima donde se emulan ataques Windows y se genera telemetría de procesos y registro."),
        ("Victim Linux\n(Servidor)", "Ubuntu Server\n192.168.56.15", "Auditd, /var/log/auth.log, Agente Wazuh", "Servidor Linux con servicios SSH expuestos para pruebas de fuerza bruta y persistencia."),
        ("Blue Team\n(SOC SIEM)", "Ubuntu / Wazuh\n192.168.56.30", "Wazuh Manager + Indexer + Dashboard Web", "Ingesta central de eventos en tiempo real, correlación de alertas y Active Response.")
    ]

    for row_idx, row in enumerate(arch_data, start=1):
        for col_idx, text in enumerate(row):
            cell = tbl_arch.cell(row_idx, col_idx)
            bg = "F9FAFB" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_after = Pt(0)
            r_cell = p_cell.add_run(text)
            r_cell.font.size = Pt(8.5)
            if col_idx == 0:
                r_cell.bold = True

    # --- SECCIÓN 3: Escenarios Clave ---
    add_custom_heading("3. Escenarios de Práctica Prácticos para el Portafolio", 1, COLOR_SECONDARY)

    scenarios = [
        {
            "num": "Escenario 1",
            "title": "Credential Access & Spraying - Fuerza Bruta SSH y Password Spraying",
            "mitre": "T1110.001 (Password Guessing) & T1110.003 (Password Spraying)",
            "red": "Ejecución de ataques de fuerza bruta a SSH con Hydra y Password Spraying contra cuentas de Windows con NetExec.",
            "telemetry": "Windows Event ID 4625 (Logon Failure) + 4624 (Success) y Linux /var/log/auth.log (sshd authentication failure).",
            "blue": "Regla de detección de umbral y regla de correlación (múltiples usuarios fallidos desde una sola IP en 2 min) + Active Response para autobloqueo de IP atacante."
        },
        {
            "num": "Escenario 2",
            "title": "Credential Access - LSASS Memory Dumping",
            "mitre": "T1003.001 - OS Credential Dumping: LSASS Memory",
            "red": "Uso de ProcDump, comsvcs.dll (MiniDump) o Mimikatz para volcar credenciales de la memoria de lsass.exe.",
            "telemetry": "Sysmon Event ID 10 (ProcessAccess con granted access 0x1010/0x1F0FFF sobre lsass.exe) y Event ID 1 (Procesos sospechosos).",
            "blue": "Regla de detección que alerte sobre accesos anómalos a LSASS provenientes de rundll32.exe, procdump.exe o ejecutables no firmados."
        },
        {
            "num": "Escenario 3",
            "title": "Persistence - Creación de Tareas Programadas Maliciosas",
            "mitre": "T1053.005 - Scheduled Task/Job: Scheduled Task",
            "red": "Creación de una tarea programada persistente usando 'schtasks /create' o PowerShell para ejecutar un script oculto.",
            "telemetry": "Windows Security Event ID 4698 (A scheduled task was created) + Sysmon Event ID 1 (schtasks.exe con comandos codificados).",
            "blue": "Regla que identifique creación de tareas programadas que invoquen 'powershell.exe -enc', 'cmd.exe /c' o rutas temporales."
        },
        {
            "num": "Escenario 4",
            "title": "Defense Evasion - Ejecución Ofuscada en PowerShell",
            "mitre": "T1059.001 - Command and Scripting Interpreter: PowerShell",
            "red": "Descarga en memoria y ejecución de payloads (IEX / DownloadString) utilizando ofuscación de cadenas y codificación Base64.",
            "telemetry": "PowerShell Script Block Logging (Event ID 4104), Transcription Logging y Sysmon Event ID 1.",
            "blue": "Regla Sigma para detectar 'Script Block Logging' con palabras clave de bypass, descarga remota web y llamadas reflection."
        }
    ]

    for s in scenarios:
        add_custom_heading(f"{s['num']}: {s['title']}", 2, COLOR_PRIMARY)
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)
        r_mitre = sp.add_run(f"📌 MITRE ATT&CK: {s['mitre']}\n")
        r_mitre.bold = True
        r_mitre.font.color.rgb = COLOR_PURPLE

        r_red_lbl = sp.add_run("⚔️ Red Team (Ataque): ")
        r_red_lbl.bold = True
        r_red_lbl.font.color.rgb = COLOR_SECONDARY
        sp.add_run(f"{s['red']}\n")

        r_tel_lbl = sp.add_run("🔍 Telemetría Requerida: ")
        r_tel_lbl.bold = True
        r_tel_lbl.font.color.rgb = COLOR_BLUE_TEAM
        sp.add_run(f"{s['telemetry']}\n")

        r_blue_lbl = sp.add_run("🛡️ Blue Team (Detección & SIEM): ")
        r_blue_lbl.bold = True
        r_blue_lbl.font.color.rgb = COLOR_PRIMARY
        sp.add_run(f"{s['blue']}")

    # --- SECCIÓN 4: Glosario de Términos ---
    add_custom_heading("4. Glosario Fundamental de Ciberseguridad (SOC & Purple Team)", 1, COLOR_PRIMARY)
    p_glos = doc.add_paragraph()
    p_glos.add_run("Este glosario define los conceptos técnicos clave utilizados a lo largo del laboratorio y en entrevistas laborales:")

    glossary_terms = [
        ("SOC (Security Operations Center): ", "Equipo centralizado de personas, procesos y tecnología encargado de monitorear, detectar, analizar y responder a incidentes de ciberseguridad en tiempo real."),
        ("Purple Team: ", "Metodología colaborativa donde los atacantes (Red Team) y los defensores (Blue Team) trabajan juntos para probar defensas, identificar brechas y mejorar las reglas de detección."),
        ("SIEM (Security Information & Event Management): ", "Plataforma central (ej. Wazuh, Splunk, Elastic) que recolecta, almacena, correlaciona y analiza logs de toda la infraestructura para generar alertas de seguridad."),
        ("EDR / XDR (Endpoint Detection & Response): ", "Software instalado en los dispositivos finales (endpoints) que monitorea continuamente el comportamiento del sistema, detecta anomalías y permite aislar el equipo ante un ataque."),
        ("Telemetría: ", "Conjunto de datos y registros detallados (creación de procesos, conexiones de red, accesos a memoria, cambios de registro) generados por el sistema operativo y sus sensores."),
        ("Sysmon (System Monitor): ", "Herramienta de Microsoft (Sysinternals) que se instala como servicio y controlador de dispositivo en Windows para registrar telemetría profunda que los logs nativos no capturan."),
        ("MITRE ATT&CK: ", "Base de conocimiento global y accesible de tácticas, técnicas y procedimientos (TTPs) de adversarios basada en observaciones del mundo real."),
        ("Atomic Red Team: ", "Biblioteca de pruebas de seguridad atómicas, simples y portables creadas por Red Canary para validar el funcionamiento de las detecciones de seguridad."),
        ("Detection-as-Code (Sigma): ", "Enfoque moderno donde las reglas de detección se escriben en código estándar (archivos YAML de Sigma), se versionan en Git y se traducen automáticamente al SIEM."),
        ("LSASS (Local Security Authority Subsystem Service): ", "Proceso crítico de Windows (lsass.exe) que gestiona la autenticación de usuarios y almacena credenciales en memoria; objetivo principal de atacantes."),
        ("Password Spraying: ", "Técnica de ataque donde se prueba una sola contraseña común contra muchos nombres de usuario diferentes para evitar el bloqueo de cuentas por exceso de intentos fallidos."),
        ("Active Response / SOAR: ", "Capacidad del SIEM de ejecutar acciones automáticas de respuesta ante una alerta (por ejemplo, bloquear una IP en el firewall o finalizar un proceso malicioso).")
    ]

    for term, definition in glossary_terms:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r1 = bp.add_run(term)
        r1.bold = True
        r1.font.color.rgb = COLOR_BLUE_TEAM
        bp.add_run(definition)

    # --- SECCIÓN 5: Estrategia LinkedIn ---
    add_custom_heading("5. Estrategia de Marca Personal y Publicación en LinkedIn", 1, COLOR_PURPLE)
    li_points = [
        ("Estructura del Repositorio en GitHub: ", "README con diagrama de arquitectura, matriz de cobertura MITRE ATT&CK interactiva, carpetas '/detections' (reglas Sigma) y '/evidence' (capturas SIEM)."),
        ("Publicaciones Tipo Caso de Estudio: ", "'Cómo emulé la técnica MITRE T1110.003 (Password Spraying) y construí una regla de detección correlacionada en Wazuh con respuesta activa.'"),
        ("Material Visual de Alto Impacto: ", "Incluir 3-4 capturas clave: diagrama de topología, ejecución en Atomic Red Team, evento Sysmon en crudo y dashboard del SIEM con la alerta disparada.")
    ]
    for bold_text, normal_text in li_points:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(3)
        r1 = bp.add_run(bold_text)
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        bp.add_run(normal_text)

    doc.save(output_path)
    print(f"Documento completo generado exitosamente en: {output_path}")

if __name__ == "__main__":
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    create_proposal_docx(
        os.path.join(docs_dir, "Propuesta_Laboratorio_SOC_PurpleTeam.docx"),
        os.path.join(docs_dir, "network_diagram.png")
    )
