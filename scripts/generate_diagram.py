import os
from PIL import Image, ImageDraw, ImageFont

def get_font(name, size):
    paths = [
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{name}.ttf",
        f"/usr/share/fonts/truetype/ubuntu/Ubuntu-{name}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{name}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def draw_network_diagram(output_path):
    width, height = 1600, 920
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255)) # Slate 900
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font("Bold", 32)
    font_subtitle = get_font("Regular", 16)
    font_card_title = get_font("Bold", 18)
    font_card_sub = get_font("Bold", 14)
    font_card_body = get_font("Regular", 13)
    font_badge = get_font("Bold", 12)
    font_conn = get_font("Bold", 12)

    # Background grid effect
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(30, 41, 59, 120), width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(30, 41, 59, 120), width=1)

    # Header Banner
    draw.rounded_rectangle([(40, 30), (width - 40, 110)], radius=12, fill=(30, 41, 59, 220), outline=(71, 85, 105, 255), width=2)
    draw.text((60, 42), "SYSCOW PURPLE TEAM SOC LAB — ARQUITECTURA DE RED", font=font_title, fill=(241, 245, 249, 255))
    draw.text((60, 80), "Simulación de Adversarios (MITRE ATT&CK) • Telemetría Sysmon • SIEM/EDR Wazuh • Detección Sigma", font=font_subtitle, fill=(148, 163, 184, 255))

    # Main Lab Boundary Box
    draw.rounded_rectangle([(40, 130), (width - 40, 800)], radius=16, fill=(17, 24, 39, 200), outline=(51, 65, 85, 255), width=2)
    
    # Lab Box Tag
    draw.rounded_rectangle([(60, 140), (460, 172)], radius=6, fill=(99, 102, 241, 230))
    draw.text((70, 146), "VIRTUALBOX PRIVATE HOST-ONLY NETWORK: 192.168.56.0/24", font=font_badge, fill=(255, 255, 255, 255))

    # Helper function for Node Cards
    def draw_node_card(x, y, w, h, title, ip, role_badge, role_color, items, border_color, header_bg):
        # Card body
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=12, fill=(30, 41, 59, 240), outline=border_color, width=2)
        # Header bar
        draw.rounded_rectangle([(x, y), (x + w, y + 55)], radius=12, fill=header_bg)
        # Fix bottom corners of header
        draw.rectangle([(x, y + 40), (x + w, y + 55)], fill=header_bg)
        draw.line([(x, y + 55), (x + w, y + 55)], fill=border_color, width=1)
        
        # Title and IP
        draw.text((x + 16, y + 12), title, font=font_card_title, fill=(255, 255, 255, 255))
        draw.text((x + 16, y + 34), f"IP: {ip} (vboxnet0) | Dual NAT", font=font_card_body, fill=(203, 213, 225, 255))
        
        # Role Badge
        badge_w = 110
        draw.rounded_rectangle([(x + w - badge_w - 12, y + 14), (x + w - 12, y + 42)], radius=6, fill=role_color)
        draw.text((x + w - badge_w - 2, y + 21), role_badge, font=font_badge, fill=(255, 255, 255, 255))

        # Items list
        curr_y = y + 70
        for cat, val in items:
            draw.text((x + 16, curr_y), f"• {cat}:", font=font_card_sub, fill=(148, 163, 184, 255))
            draw.text((x + 30, curr_y + 18), val, font=font_card_body, fill=(241, 245, 249, 255))
            curr_y += 42

    # --- NODE 1: RED TEAM (Attacker) ---
    red_items = [
        ("Sistema Operativo", "Kali Linux (2026.x) - 4GB RAM"),
        ("Herramientas Ataque", "Atomic Red Team, Hydra, NetExec"),
        ("TTPs Emulados", "T1110 (Brute Force), T1003 (LSASS)"),
        ("Movimiento Lateral", "T1059 (PowerShell), T1053 (Tasks)")
    ]
    draw_node_card(70, 200, 360, 260, "RED TEAM (Atacante)", "192.168.56.20", "OFFENSIVE", (220, 38, 38, 255), red_items, (239, 68, 68, 255), (153, 27, 27, 240))

    # --- NODE 2: VICTIM WINDOWS ---
    win_items = [
        ("Sistema Operativo", "Windows 11 Enterprise - 6GB RAM"),
        ("Sensores / Logging", "Sysmon v15 (SwiftOnSecurity config)"),
        ("Auditoría Avanzada", "Script Block Logging (Event ID 4104)"),
        ("Agente EDR", "Wazuh Windows Agent (v4.14+)")
    ]
    draw_node_card(600, 200, 380, 260, "VICTIM (Windows Endpoint)", "192.168.56.10", "TELEMETRY", (37, 99, 235, 255), win_items, (59, 130, 246, 255), (30, 58, 138, 240))

    # --- NODE 3: VICTIM LINUX ---
    lin_items = [
        ("Sistema Operativo", "Ubuntu Server - 2-4GB RAM"),
        ("Sensores / Logging", "Auditd, /var/log/auth.log"),
        ("Servicios Expuestos", "SSH (Puerto 22), Web Nginx"),
        ("Agente EDR", "Wazuh Linux Agent (v4.14+)")
    ]
    draw_node_card(600, 500, 380, 260, "VICTIM (Linux Server)", "192.168.56.15", "TELEMETRY", (13, 148, 136, 255), lin_items, (20, 184, 166, 255), (19, 78, 74, 240))

    # --- NODE 4: BLUE TEAM / SOC SIEM ---
    soc_items = [
        ("Core SIEM & XDR", "Wazuh Manager + OpenSearch"),
        ("Visualización", "Wazuh Dashboard Web (HTTPS / 443)"),
        ("Reglas de Detección", "Reglas Sigma (YAML) + XML Custom"),
        ("Respuesta Activa", "Active Response (IP / Host Isolation)")
    ]
    draw_node_card(1130, 330, 390, 270, "BLUE TEAM (SOC SIEM)", "192.168.56.30", "DEFENSIVE", (124, 58, 237, 255), soc_items, (168, 85, 247, 255), (91, 33, 182, 240))

    # --- FLOW CONNECTIONS & ARROWS ---
    # 1. Attack Traffic: Red Team -> Windows Victim
    draw.line([(430, 280), (600, 280)], fill=(239, 68, 68, 255), width=3)
    draw.polygon([(595, 274), (605, 280), (595, 286)], fill=(239, 68, 68, 255))
    draw.rounded_rectangle([(445, 255), (585, 276)], radius=4, fill=(30, 41, 59, 255), outline=(239, 68, 68, 200), width=1)
    draw.text((450, 258), "TTPs / Atomics", font=font_conn, fill=(248, 113, 113, 255))

    # 2. Attack Traffic: Red Team -> Linux Victim
    draw.line([(430, 380), (515, 380), (515, 580), (600, 580)], fill=(239, 68, 68, 255), width=3)
    draw.polygon([(595, 574), (605, 580), (595, 586)], fill=(239, 68, 68, 255))
    draw.rounded_rectangle([(445, 555), (585, 576)], radius=4, fill=(30, 41, 59, 255), outline=(239, 68, 68, 200), width=1)
    draw.text((452, 558), "SSH Brute Force", font=font_conn, fill=(248, 113, 113, 255))

    # 3. Telemetry Traffic: Windows -> Wazuh SIEM
    draw.line([(980, 280), (1055, 280), (1055, 420), (1130, 420)], fill=(59, 130, 246, 255), width=3)
    draw.polygon([(1125, 414), (1135, 420), (1125, 426)], fill=(59, 130, 246, 255))
    draw.rounded_rectangle([(1000, 335), (1110, 356)], radius=4, fill=(30, 41, 59, 255), outline=(59, 130, 246, 200), width=1)
    draw.text((1006, 338), "Logs (Sysmon)", font=font_conn, fill=(96, 165, 250, 255))

    # 4. Telemetry Traffic: Linux -> Wazuh SIEM
    draw.line([(980, 580), (1055, 580), (1055, 480), (1130, 480)], fill=(20, 184, 166, 255), width=3)
    draw.polygon([(1125, 474), (1135, 480), (1125, 486)], fill=(20, 184, 166, 255))
    draw.rounded_rectangle([(1000, 520), (1110, 541)], radius=4, fill=(30, 41, 59, 255), outline=(20, 184, 166, 200), width=1)
    draw.text((1006, 523), "Logs (Auditd)", font=font_conn, fill=(45, 212, 191, 255))

    # Footer / Legend Bar
    draw.rounded_rectangle([(40, 820), (width - 40, 890)], radius=10, fill=(30, 41, 59, 220), outline=(71, 85, 105, 255), width=1)
    draw.text((60, 836), "LEYENDA DEL FLUJO:", font=font_card_sub, fill=(241, 245, 249, 255))
    
    # Legend 1: Red
    draw.rectangle([(230, 842), (255, 846)], fill=(239, 68, 68, 255))
    draw.text((265, 838), "Ataques / Emulación (Red Team)", font=font_card_body, fill=(203, 213, 225, 255))

    # Legend 2: Blue/Cyan
    draw.rectangle([(550, 842), (575, 846)], fill=(59, 130, 246, 255))
    draw.text((585, 838), "Telemetría Encriptada (Agente Wazuh :1514)", font=font_card_body, fill=(203, 213, 225, 255))

    # Legend 3: Purple
    draw.rectangle([(910, 842), (935, 846)], fill=(168, 85, 247, 255))
    draw.text((945, 838), "Consola SOC & Detección (HTTPS Web Browser :443)", font=font_card_body, fill=(203, 213, 225, 255))

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    print(f"Diagrama de red generado con éxito en: {output_path}")

if __name__ == "__main__":
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    draw_network_diagram(os.path.join(docs_dir, "network_diagram.png"))
