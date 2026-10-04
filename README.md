# 🟣 SOC & Purple Team Enterprise Simulation Lab
> **Adversary Emulation (Red) + Detection Engineering & SIEM Analytics (Blue)**
> *Entorno corporativo de simulación ofensiva y defensiva para el aprendizaje práctico y la creación de casos de estudio de ciberseguridad profesional.*

---

## 🎯 Objetivo General
Construir y operar un laboratorio integral donde se emulan técnicas reales de adversarios (**MITRE ATT&CK**) y simultáneamente se instrumenta telemetría profunda de endpoints (**Sysmon, Windows Event Logs, Auditd**) e ingesta en un **SIEM/EDR** moderno (**Wazuh All-in-One**), desarrollando reglas de detección (**Sigma / Detection-as-Code**) y documentando el ciclo completo en formato de casos de estudio para **LinkedIn y GitHub**.

---

## 📁 Estructura del Proyecto
```
purple-team-soc-lab/
├── docs/
│   ├── BASE_DE_CONOCIMIENTO.md                    # Runbook técnico de herramientas, comandos y telemetría
│   ├── Base_De_Conocimiento.docx                  # Runbook técnico en formato Word
│   ├── ESTADO_DEL_PROYECTO.md                     # Registro detallado del estado y avances
│   ├── Estado_Del_Proyecto.docx                   # Registro formal en formato Word
│   ├── Propuesta_Laboratorio_SOC_PurpleTeam.docx   # Documento formal de propuesta
│   ├── Detection_Engineering_CheatSheet.docx      # Chuleta de ingeniería de detección
│   ├── Glosario_Ciberseguridad.docx               # Glosario técnico de términos clave
│   └── Guia_Plantillas_LinkedIn.docx              # Plantillas para publicaciones de LinkedIn
├── detections/                                    # Reglas Sigma (YAML) y reglas personalizadas Wazuh
├── evidence/                                      # Capturas de telemetría, logs y dashboards
├── playbooks/                                     # Procedimientos de respuesta a incidentes (SOPs)
├── scripts/
│   ├── patch_vbox_kernel7.sh                      # Parche de compatibilidad VirtualBox para Kernel 7.0+
│   ├── generate_all_docx.py                       # Generador automatizado de documentos DOCX
│   └── generate_diagram.py                        # Generador visual de diagramas de red
└── README.md
```

---

## 🏗️ Topología del Laboratorio (Red Dual-NIC)

El laboratorio opera bajo un esquema de **Doble Adaptador**:
* **Adaptador 1 (NAT):** Salida a internet para descarga de paquetes y herramientas.
* **Adaptador 2 (Host-Only `vboxnet0`):** Subred privada aislada `192.168.56.0/24` donde ocurren las emulaciones y el tráfico de telemetría.

```
                          HOST UBUNTU (192.168.56.1)
             +---------------------------------------------------+
             |  Control Central, Navegador SOC & Hipervisor      |
             +-------------------------+-------------------------+
                                       | (Red vboxnet0 / 192.168.56.0/24)
         +-----------------------------+-----------------------------+
         |                             |                             |
         v                             v                             v
+------------------+         +-------------------+         +-------------------+
|  RED TEAM (Kali) |         |  VÍCTIMA WINDOWS  |         |  VÍCTIMA LINUX    |
|  192.168.56.20   |         |  192.168.56.10    |         |  192.168.56.15    |
|  Atomic Red Team |         |  Windows 11 Pro   |         |  Ubuntu Server    |
|  Hydra, Nmap     |         |  Sysmon + Scripts |         |  OWASP Juice Shop |
+--------+---------+         +---------+---------+         +---------+---------+
         |                             |                             |
         | TTPs / Ataques              | Logs / Telemetría           | Logs Web/SSH
         |                             v                             v
         |                   +-------------------------------------------------+
         +------------------>|            BLUE TEAM SOC (Wazuh Server)         |
                             |            192.168.56.30                        |
                             |  Indexer (OpenSearch) + Manager + Web Dashboard |
                             +-------------------------------------------------+
```

| Componente | VM en VirtualBox | IP Lab (`vboxnet0`) | Rol Principal |
| :--- | :--- | :--- | :--- |
| **Blue Team SOC** | `Ubuntu Server Wazuh` | `192.168.56.30` | Ingesta de telemetría, correlación en tiempo real y alertas SIEM |
| **Víctima Windows** | `Windows 11` | `192.168.56.10` | Endpoint instrumentado con Microsoft Sysmon y PowerShell ScriptBlockLogging |
| **Víctima Linux** | `Ubuntu Server` | `192.168.56.15` | Servidor web vulnerable con OWASP Juice Shop y servicios Linux |
| **Red Team** | `kali-linux-2026.2` | `192.168.56.20` | Emulador de ataques y técnicas de adversarios (MITRE ATT&CK) |

---

## 📊 Estado Actual de los Hitos

- [x] **Hipervisor & Kernel:** Módulos de VirtualBox 7.2.6 parcheados y compilados con éxito para Kernel Linux 7.0+ ([`patch_vbox_kernel7.sh`](file:///home/anfrimax/Desktop/purple-team-soc-lab/scripts/patch_vbox_kernel7.sh)).
- [x] **Víctima Windows 11:** Máquina creada con EFI, TPM 2.0 y Guest Additions.
- [x] **Telemetría Endpoint:** Microsoft Sysmon64 instalado con la configuración de SwiftOnSecurity y auditoría de PowerShell habilitada.
- [x] **Servidor SIEM:** VM `Ubuntu Server Wazuh` desplegada e instalación completa de Wazuh All-in-One 4.9.x finalizada.
- [x] **Dashboard SOC & Acceso Web:** Interfaz web HTTPS (`https://192.168.56.30`) operativa y verificada desde el host.
- [x] **Agente Windows 11 Conectado:** Agente `wazuh-agent 4.9.2` registrado y en estado **Active** (ID: 001, `DESKTOP-TS224KA`, IP `192.168.56.10`).
- [x] **Agente Linux Víctima Conectado:** Agente `wazuh-agent 4.9.2` registrado y en estado **Active** (ID: 002, `ubuntu-victim`, IP `192.168.56.15`).
- [x] **Red y Sincronización Horaria:** IPs estáticas homologadas, Dual-NIC habilitado en todos los nodos y sincronización NTP activa.
- [x] **Reconocimiento & Network Service Discovery (MITRE T1046):** Escaneo de superficie con Nmap completado contra la víctima Linux, descubriendo puertos 22 (SSH) y 3000 (Juice Shop).
- [x] **Caso de Estudio 1 - Intrusión & Brute Force (MITRE T1110.001):** Emulación de fuerza bruta SSH con Hydra desde Kali + Detección SIEM en Wazuh (Reglas 5760 y 100010 Nivel 10) + Regla Sigma ([`lnx_sshd_session_brute_force.yml`](file:///home/anfrimax/Desktop/purple-team-soc-lab/detections/sigma/linux/lnx_sshd_session_brute_force.yml)) + Playbook IR ([`PB-01_BruteForce_SSH.md`](file:///home/anfrimax/Desktop/purple-team-soc-lab/playbooks/PB-01_BruteForce_SSH.md)).
- [x] **Mitigación Defensiva (Active Response):** Bloqueo dinámico automatizado de IP atacante (`192.168.56.20`) en `iptables` vía Wazuh `firewall-drop` verificado en tiempo real ([`05_iptables_firewall_drop.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/05_iptables_firewall_drop.png)).
- [ ] **Caso de Estudio 2 - Windows Credential Access (MITRE T1003.001):** Dump de memoria LSASS con telemetría Sysmon EID 10 en Windows 11.

Para más detalles, consulta el documento completo de [ESTADO_DEL_PROYECTO.md](file:///home/anfrimax/Desktop/purple-team-soc-lab/docs/ESTADO_DEL_PROYECTO.md).
