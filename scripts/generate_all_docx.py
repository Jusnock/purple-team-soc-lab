import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

COLOR_PRIMARY = RGBColor(0x1B, 0x36, 0x5D)    # Navy Blue
COLOR_SECONDARY = RGBColor(0x8B, 0x00, 0x00)  # Crimson
COLOR_BLUE_TEAM = RGBColor(0x00, 0x5C, 0x8A)  # Steel Blue
COLOR_PURPLE = RGBColor(0x5E, 0x24, 0x8C)     # Purple Team

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

def init_doc(title, subtitle):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_t = p_title.add_run(title)
    r_t.font.size = Pt(18)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_PRIMARY

    if subtitle:
        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(14)
        r_s = p_sub.add_run(subtitle)
        r_s.font.size = Pt(11)
        r_s.font.italic = True
        r_s.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    return doc

def add_heading(doc, text, level=1, color=COLOR_PRIMARY):
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

# 1. Glosario DOCX
def generate_glosario_docx(out_path):
    doc = init_doc("Glosario Fundamental de Ciberseguridad", "Términos Clave de SOC, EDR, SIEM, Purple Team y Detection Engineering")
    
    add_heading(doc, "1. Conceptos de Operaciones de Seguridad (Blue Team)", 1, COLOR_BLUE_TEAM)
    blue_terms = [
        ("SOC (Security Operations Center)", "Equipo centralizado de personas, procesos y tecnología responsable de monitorear, detectar, analizar y responder a incidentes de seguridad las 24/7."),
        ("SIEM (Security Information & Event Management)", "Plataforma central (como Wazuh, Splunk, Elastic) que ingesta logs de múltiples fuentes, los normaliza, correlaciona eventos en tiempo real y dispara alertas."),
        ("EDR / XDR (Endpoint Detection & Response)", "Agente instalado en los endpoints que monitorea procesos, archivos y memoria para detectar anomalías y permitir aislamiento inmediato de la red."),
        ("Telemetría", "Conjunto de datos y registros detallados (creación de procesos, conexiones de red, accesos a memoria, cambios de registro) generados por el sistema operativo y sensores."),
        ("Sysmon (System Monitor)", "Servicio y controlador de Microsoft (Sysinternals) para Windows que aporta telemetría profunda de procesos y red que los registros nativos no capturan."),
        ("Detection Engineering", "Disciplina de diseñar, probar y afinar reglas de detección como código para identificar TTPs adversarios minimizando falsos positivos."),
        ("Sigma (Detection-as-Code)", "Formato estándar en YAML para describir reglas de detección de manera neutral e independiente del SIEM."),
        ("Active Response / SOAR", "Capacidad de ejecutar acciones defensivas automáticas ante una alerta (ej. bloquear una IP en el firewall o finalizar un proceso).")
    ]
    for term, desc in blue_terms:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{term}: ")
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        p.add_run(desc)

    add_heading(doc, "2. Conceptos de Emulación Ofensiva (Red Team)", 1, COLOR_SECONDARY)
    red_terms = [
        ("Purple Team", "Metodología colaborativa donde atacantes y defensores trabajan juntos para probar defensas, validar telemetría y crear detecciones precisas."),
        ("MITRE ATT&CK Framework", "Base de conocimiento global y estructurada de tácticas, técnicas y procedimientos (TTPs) de adversarios basada en ataques reales."),
        ("TTPs (Tactics, Techniques & Procedures)", "Patrones de comportamiento, métodos operativos y herramientas que utiliza un adversario."),
        ("Atomic Red Team", "Biblioteca de pruebas de seguridad atómicas, portables y reproducibles creadas por Red Canary para validar reglas de detección."),
        ("LSASS (Local Security Authority Subsystem Service)", "Proceso de Windows (lsass.exe) que gestiona la autenticación de usuarios y almacena credenciales en memoria. Objetivo prioritario en ataques T1003.001."),
        ("Password Spraying (T1110.003)", "Técnica de ataque donde se prueba una sola contraseña común contra una lista extensa de usuarios para evadir el bloqueo de cuentas."),
        ("Defense Evasion", "Técnicas que los atacantes emplean para no ser detectados (ofuscación de scripts, descarga en memoria, evasión de antivirus).")
    ]
    for term, desc in red_terms:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{term}: ")
        r.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        p.add_run(desc)

    doc.save(out_path)

# 2. Cheat Sheet DOCX
def generate_cheatsheet_docx(out_path):
    doc = init_doc("Detection Engineering & Telemetry Cheat Sheet", "Guía Rápida de Event IDs Críticos de Windows, Sysmon y Sintaxis Sigma")
    
    add_heading(doc, "1. Windows Security Event Logs Críticos", 1, COLOR_PRIMARY)
    tbl_win = doc.add_table(rows=8, cols=3)
    tbl_win.alignment = WD_TABLE_ALIGNMENT.CENTER
    win_headers = ["Event ID", "Canal / Nombre", "Caso de Uso en el SOC"]
    for i, h in enumerate(win_headers):
        c = tbl_win.cell(0, i)
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)

    win_data = [
        ("4624", "Successful Logon", "Detección de logons anómalos o éxito post-fuerza bruta."),
        ("4625", "Failed Logon", "Detección de ataques de fuerza bruta y Password Spraying."),
        ("4688", "Process Creation", "Creación de procesos nativa (requiere auditoría de línea de comando)."),
        ("4698", "Scheduled Task Created", "Persistencia mediante tareas programadas maliciosas."),
        ("4720", "User Account Created", "Creación de cuentas locales no autorizadas (Backdoors)."),
        ("4740", "Account Locked Out", "Cuentas bloqueadas tras superar umbral de intentos fallidos."),
        ("4104", "PowerShell Script Block", "Captura del código real de scripts PowerShell ejecutados (incluso ofuscados).")
    ]
    for row_idx, row in enumerate(win_data, start=1):
        for col_idx, text in enumerate(row):
            c = tbl_win.cell(row_idx, col_idx)
            set_cell_background(c, "F9FAFB" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    add_heading(doc, "2. Microsoft Sysmon Event IDs (Telemetría de Alta Fidelidad)", 1, COLOR_BLUE_TEAM)
    tbl_sys = doc.add_table(rows=8, cols=3)
    tbl_sys.alignment = WD_TABLE_ALIGNMENT.CENTER
    sys_headers = ["Sysmon ID", "Nombre del Evento", "Mapeo MITRE / Utilidad"]
    for i, h in enumerate(sys_headers):
        c = tbl_sys.cell(0, i)
        set_cell_background(c, "005C8A")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)

    sys_data = [
        ("Event ID 1", "Process Creation", "Creación de procesos con línea de comando completa, hash SHA256 y ParentImage."),
        ("Event ID 3", "Network Connection", "Conexiones TCP/UDP iniciadas por procesos con IP y puerto destino."),
        ("Event ID 7", "Image Loaded", "DLLs cargadas por un proceso (detección de DLL Hijacking / Injection)."),
        ("Event ID 8", "CreateRemoteThread", "Inyección de hilos en procesos remotos (Process Injection / Hollowing)."),
        ("Event ID 10", "ProcessAccess", "Apertura y lectura de memoria de procesos (Acceso a lsass.exe - T1003.001)."),
        ("Event ID 11", "FileCreate", "Creación de archivos sospechosos en AppData/Temp (Droppers/Payloads)."),
        ("Event ID 12/13", "RegistryEvent", "Modificación o creación de claves de inicio automático (Run/RunOnce).")
    ]
    for row_idx, row in enumerate(sys_data, start=1):
        for col_idx, text in enumerate(row):
            c = tbl_sys.cell(row_idx, col_idx)
            set_cell_background(c, "F9FAFB" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    add_heading(doc, "3. Ejemplo de Estructura de Regla Sigma (YAML)", 1, COLOR_PURPLE)
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(4)
    r_c = p_code.add_run(
        "title: Suspicious LSASS Memory Access via ProcessAccess\n"
        "id: 5a7e1f4b-1234-5678-9abc-def012345678\n"
        "status: experimental\n"
        "description: Detecta accesos sospechosos a lsass.exe para volcado de credenciales.\n"
        "tags:\n"
        "    - attack.credential_access\n"
        "    - attack.t1003.001\n"
        "logsource:\n"
        "    category: process_access\n"
        "    product: windows\n"
        "detection:\n"
        "    selection:\n"
        "        TargetImage|endswith: '\\lsass.exe'\n"
        "        GrantedAccess:\n"
        "            - '0x1010'\n"
        "            - '0x1F0FFF'\n"
        "    filter:\n"
        "        SourceImage|endswith:\n"
        "            - '\\svchost.exe'\n"
        "            - '\\MsMpEng.exe'\n"
        "    condition: selection and not filter\n"
        "level: high"
    )
    r_c.font.name = 'Courier New'
    r_c.font.size = Pt(8.5)
    r_c.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    doc.save(out_path)

# 3. LinkedIn Guide DOCX
def generate_linkedin_docx(out_path):
    doc = init_doc("Guía y Plantilla para Publicaciones en LinkedIn", "Estrategia de Marca Personal y Presentación de Casos de Estudio Purple Team")
    
    add_heading(doc, "1. Enfoque Estratégico para Reclutadores", 1, COLOR_PURPLE)
    p = doc.add_paragraph()
    p.add_run("Para captar la atención de reclutadores, CISOs y gerentes de SOC, los posts deben seguir una estructura de ")
    p.add_run("Caso de Estudio Técnico").bold = True
    p.add_run(" que demuestre resolución de problemas reales:")

    points = [
        ("Título Claro con Mapeo MITRE: ", "Usa la nomenclatura oficial (ej. T1110.003 Password Spraying o T1003.001 LSASS Dumping)."),
        ("Estructura Red vs Blue: ", "Explica brevemente qué técnica ofensiva simulaste y qué regla defensiva diseñaste."),
        ("Evidencia Visual (4 imágenes): ", "Diagrama del Lab + Comando en terminal + Log en crudo + Alerta en el SIEM."),
        ("Enlace a GitHub: ", "Incluye siempre el repositorio con el código de las reglas Sigma y el Write-up.")
    ]
    for bold_t, norm_t in points:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(bold_t)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        bp.add_run(norm_t)

    add_heading(doc, "2. Plantilla Lista para Copiar y Rellenar", 1, COLOR_PRIMARY)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    set_cell_background(c, "F0F4F8")
    set_cell_margins(c, 100, 100, 140, 140)
    p_box = c.paragraphs[0]
    p_box.paragraph_format.space_after = Pt(0)
    
    plantilla_text = (
        "🚀 [PURPLE TEAM CASE STUDY]: Emulando y Detectando [Nombre de la Técnica] (MITRE ATT&CK [ID_TECNICA])\n\n"
        "¿Cómo detecta un SOC un ataque de [Técnica, ej. Password Spraying / LSASS Dumping] antes de comprometer la red?\n\n"
        "En mi laboratorio de simulación Purple Team, implementé el ciclo completo de emulación y Detection Engineering:\n\n"
        "⚔️ Perspectiva Ofensiva (Red Team):\n"
        "• Emulé la técnica [ID_TECNICA] utilizando [Herramienta, ej. Atomic Red Team / Hydra / NetExec].\n"
        "• Se generaron [ej. 50 intentos de logon contra cuentas / volcado de memoria de lsass.exe].\n\n"
        "🔍 Análisis de Telemetría (Blue Team):\n"
        "• Identifiqué que los logs nativos eran insuficientes y configuré [Sysmon Event ID 10 / Script Block Logging 4104 / Auditd].\n\n"
        "🛡️ Detection Engineering & SIEM:\n"
        "• Redacté una regla de detección en formato estándar Sigma (YAML).\n"
        "• La integré en Wazuh SIEM para correlación en tiempo real.\n"
        "• Configuré Active Response para autobloqueo de la IP atacante.\n\n"
        "📊 Resultados: 0% de evasión en el re-test y reducción de falsos positivos.\n"
        "📂 Repositorio con reglas y logs: [Enlace a GitHub]\n\n"
        "#Cybersecurity #PurpleTeam #SOC #DetectionEngineering #MITREATTCK #Wazuh #Sysmon"
    )
    r_pt = p_box.add_run(plantilla_text)
    r_pt.font.size = Pt(8.5)

    doc.save(out_path)

# 4. Project State DOCX
def generate_project_state_docx(out_path):
    doc = init_doc("Estado del Proyecto & Contexto del Laboratorio", "Registro de Configuración de Hardware, Topología de Red y Siguientes Pasos")
    
    add_heading(doc, "1. Especificaciones de Hardware del Host", 1, COLOR_PRIMARY)
    specs = [
        ("Procesador: ", "Intel Core Ultra 7 (Arquitectura híbrida de alto rendimiento)"),
        ("Memoria RAM: ", "32 GB RAM DDR5"),
        ("Almacenamiento: ", "SSD NVMe de alta velocidad (>250 GB libres)"),
        ("Sistema Operativo Host: ", "Ubuntu 26.04.1 LTS (Resolute) con Kernel Linux 7.0"),
        ("Hipervisor: ", "VirtualBox 7.2.6 (Módulos de kernel parcheados con éxito para Kernel 7.0+)"),
        ("Red Host-Only: ", "vboxnet0 activa en 192.168.56.1/24 con rango estático libre (.2 a .99)")
    ]
    for k, v in specs:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(k)
        r.bold = True
        r.font.color.rgb = COLOR_BLUE_TEAM
        p.add_run(v)

    add_heading(doc, "2. Nodos y Topología del Laboratorio (Esquema Dual-NIC)", 1, COLOR_PRIMARY)
    tbl = doc.add_table(rows=5, cols=5)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Nodo / VM", "IP Lab (vboxnet0)", "IP Internet (NAT)", "RAM / vCPU", "Rol y Herramientas"]
    for i, h in enumerate(headers):
        c = tbl.cell(0, i)
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8.5)

    nodes = [
        ("Windows 11 Pro", "192.168.56.10", "DHCP (NAT)", "6 GB / 4 vCPU", "Víctima Windows: Sysmon + ScriptBlockLogging + Wazuh Agent (ID: 001, Active)"),
        ("Ubuntu Server Wazuh", "192.168.56.30", "DHCP (NAT)", "6 GB / 4 vCPU", "Blue Team SOC: Wazuh 4.9.x (Indexer + Manager + Dashboard HTTPS + API 55000)"),
        ("Ubuntu Server", "192.168.56.15", "DHCP (NAT)", "4 GB / 4 vCPU", "Víctima Linux: OWASP Juice Shop + SSH + Wazuh Agent (ID: 002, Active)"),
        ("Kali Linux", "192.168.56.20", "DHCP (NAT)", "4 GB / 7 vCPU", "Red Team: Atomic Red Team, Hydra, Nmap, NetExec, Python (Operativo)")
    ]
    for row_idx, row in enumerate(nodes, start=1):
        for col_idx, text in enumerate(row):
            c = tbl.cell(row_idx, col_idx)
            set_cell_background(c, "F9FAFB" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True

    add_heading(doc, "3. Hitos de Infraestructura y Casos de Estudio Completados", 1, COLOR_PURPLE)
    completed = [
        ("Compatibilidad del Hipervisor: ", "Parcheo y compilación de módulos VirtualBox en Kernel Linux 7.0+ (scripts/patch_vbox_kernel7.sh)."),
        ("Despliegue de Víctima Windows: ", "Aprovisionamiento de Windows 11 Pro con UEFI/EFI64, TPM 2.0 y Guest Additions."),
        ("Instrumentación de Telemetría: ", "Microsoft Sysmon con sysmonconfig de SwiftOnSecurity y activación de PowerShell Script Block Logging (EID 4104)."),
        ("Despliegue del Servidor SIEM: ", "Ubuntu Server Wazuh operativo con Indexer, Manager, Dashboard y Filebeat (puertos 443, 1514, 1515 y 55000 activos)."),
        ("Enrolamiento de Agentes Windows y Linux: ", "Agente Windows 11 (ID: 001) y Ubuntu Server (ID: 002) enrolados y en estado Active en Wazuh Dashboard."),
        ("Sincronización Horaria (NTP): ", "Timezone unificado America/Argentina/Buenos_Aires y systemd-timesyncd activo en todos los nodos."),
        ("Reconocimiento de Red (MITRE T1046): ", "Escaneo focalizado con Nmap (-sV -Pn) desde Kali contra 192.168.56.15 identificando SSH (22) y Juice Shop (3000)."),
        ("Caso de Estudio 1 - Fuerza Bruta SSH (MITRE T1110.001): ", "Emulación de ataque con Hydra desde Kali contra Ubuntu Server."),
        ("Telemetría Forense e Ingesta SIEM: ", "Detección de eventos sshd-session (Regla 5760 Nivel 5) y alertas correlacionadas de alta severidad (Regla 5763 Nivel 10 y Regla 5551 PAM)."),
        ("Detection Engineering & Detection-as-Code: ", "Regla neutral en formato Sigma (lnx_sshd_session_brute_force.yml), regla nativa Wazuh XML (local_rules.xml) y Playbook IR (PB-01_BruteForce_SSH.md).")
    ]
    for k, v in completed:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run("✔ " + k)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        p.add_run(v)

    add_heading(doc, "4. Roadmap Inmediato (Para la Próxima Sesión)", 1, COLOR_SECONDARY)
    steps = [
        ("Paso 1 (Mitigación Defensiva con Active Response): ", "Configurar firewall-drop en ossec.conf para autobloqueo de IP atacante en iptables tras detección de fuerza bruta."),
        ("Paso 2 (Write-Up Profesional para LinkedIn/GitHub): ", "Publicar el caso de estudio 1 con las evidencias gráficas archivadas en evidence/T1110_Password_Spraying/."),
        ("Paso 3 (Caso de Estudio 2 - Windows LSASS Memory Dump): ", "Emular dumping de credenciales (T1003.001) y analizar telemetría Sysmon EID 10 en Windows 11.")
    ]
    for k, v in steps:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(k)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        p.add_run(v)

    doc.save(out_path)

# 5. Knowledge Base DOCX
def generate_knowledge_base_docx(out_path):
    doc = init_doc("Base de Conocimiento y Runbook Técnico", "Manual de Herramientas, Comandos, Telemetría y Procedimientos Tácticos Purple Team")

    add_heading(doc, "1. Telemetría de Endpoints (Blue Team & Sensores)", 1, COLOR_BLUE_TEAM)
    add_heading(doc, "Microsoft Sysmon (System Monitor)", 2)
    p = doc.add_paragraph()
    p.add_run("Controlador del kernel (SysmonDrv.sys) y servicio para monitorizar y registrar la actividad en ")
    p.add_run("Microsoft-Windows-Sysmon/Operational").bold = True
    p.add_run(".")

    sysmon_cmds = [
        ("Instalación inicial con configuración: ", ".\\Sysmon64.exe -accepteula -i sysmonconfig.xml"),
        ("Actualizar configuración en caliente: ", ".\\Sysmon64.exe -c sysmonconfig_updated.xml"),
        ("Consultar estado y esquema activo: ", ".\\Sysmon64.exe -s"),
        ("Desinstalación completa del servicio: ", ".\\Sysmon64.exe -u")
    ]
    for k, v in sysmon_cmds:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(k)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        rc = bp.add_run(v)
        rc.font.name = 'Courier New'
        rc.font.size = Pt(8.5)

    add_heading(doc, "Event IDs Críticos de Sysmon", 2)
    tbl = doc.add_table(rows=7, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Event ID", "Nombre del Evento", "Importancia en Detección de Amenazas"]
    for i, h in enumerate(headers):
        c = tbl.cell(0, i)
        set_cell_background(c, "1B365D")
        set_cell_margins(c, 70, 70, 70, 70)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8.5)

    events = [
        ("EID 1", "Process Creation", "CommandLine, ParentImage, Hashes. Detección de árboles anómalos de procesos."),
        ("EID 3", "Network Connection", "DestinationIp, DestinationPort, Image. Conexiones a C2 y movimiento lateral."),
        ("EID 7", "Image Loaded (DLL)", "DLLs sin firmar en memoria. Detección de DLL Sideloading e inyecciones."),
        ("EID 8", "CreateRemoteThread", "Inyección de hilos remotos en procesos legítimos del sistema."),
        ("EID 10", "ProcessAccess", "Crucial: detecta accesos de lectura a lsass.exe (GrantedAccess 0x1010/0x1F0FFF)."),
        ("EID 11", "FileCreate", "Creación de payloads en carpetas temporales o de persistencia (AppData/Temp).")
    ]
    for row_idx, row in enumerate(events, start=1):
        for col_idx, text in enumerate(row):
            c = tbl.cell(row_idx, col_idx)
            set_cell_background(c, "F9FAFB" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, 50, 50, 70, 70)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True

    add_heading(doc, "2. SIEM & Monitoreo Central (Wazuh SIEM / EDR)", 1, COLOR_PURPLE)
    wazuh_cmds = [
        ("Estado de servicios en Wazuh Server: ", "sudo /var/ossec/bin/wazuh-control status"),
        ("Monitoreo de alertas en tiempo real: ", "sudo tail -f /var/ossec/logs/alerts/alerts.json | jq ."),
        ("Probar reglas de detección con logs crudos: ", "sudo /var/ossec/bin/wazuh-logtest"),
        ("Listar agentes conectados en el Manager: ", "sudo /var/ossec/bin/agent_control -l"),
        ("Enrolar agente en Windows (PowerShell): ", "msiexec /i wazuh-agent.msi /q WAZUH_MANAGER='192.168.56.30'")
    ]
    for k, v in wazuh_cmds:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(k)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        rc = bp.add_run(v)
        rc.font.name = 'Courier New'
        rc.font.size = Pt(8.5)

    add_heading(doc, "3. Emulación de Adversarios (Red Team & TTPs)", 1, COLOR_SECONDARY)
    red_cmds = [
        ("Atomic Red Team (Info de técnica): ", "Invoke-AtomicTest T1003.001 -ShowDetails"),
        ("Atomic Red Team (Ejecución): ", "Invoke-AtomicTest T1003.001 -TestNumbers 1"),
        ("Atomic Red Team (Limpieza de rastro): ", "Invoke-AtomicTest T1003.001 -Cleanup"),
        ("Hydra (Fuerza Bruta SSH): ", "hydra -L users.txt -P pass.txt -t 4 ssh://192.168.56.15"),
        ("Hydra (Password Spraying): ", "hydra -L users.txt -p 'Pass2026!' -u -t 2 ssh://192.168.56.15"),
        ("Nmap (Descubrimiento en red del lab): ", "nmap -sn 192.168.56.0/24"),
        ("Nmap (Escaneo sigiloso y versiones): ", "nmap -sS -sV -O -p- 192.168.56.10")
    ]
    for k, v in red_cmds:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(k)
        r.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        rc = bp.add_run(v)
        rc.font.name = 'Courier New'
        rc.font.size = Pt(8.5)

    doc.save(out_path)

if __name__ == "__main__":
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    generate_glosario_docx(os.path.join(docs_dir, "Glosario_Ciberseguridad.docx"))
    generate_cheatsheet_docx(os.path.join(docs_dir, "Detection_Engineering_CheatSheet.docx"))
    generate_linkedin_docx(os.path.join(docs_dir, "Guia_Plantillas_LinkedIn.docx"))
    generate_project_state_docx(os.path.join(docs_dir, "Estado_Del_Proyecto.docx"))
    generate_knowledge_base_docx(os.path.join(docs_dir, "Base_De_Conocimiento.docx"))
    print("Todos los documentos DOCX han sido generados exitosamente.")
