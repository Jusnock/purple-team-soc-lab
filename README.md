# SOC & Purple Team Simulation Lab

Laboratorio práctico de ciberseguridad enfocado en emulación de adversarios (Red Team), ingeniería de detección (Detection-as-Code) y análisis en SIEM/EDR (Blue Team) mapeado a la matriz MITRE ATT&CK.

El objetivo del proyecto es reproducir técnicas reales de ataque en un entorno controlado, analizar la telemetría generada en endpoints Windows y Linux, y construir reglas de detección precisas (Sigma / Wazuh) junto con playbooks de respuesta a incidentes.

---

## Estructura del Repositorio

```
purple-team-soc-lab/
├── detections/           # Reglas Sigma (YAML) y reglas personalizadas de Wazuh (XML)
├── docs/                 # Documentación técnica, base de conocimiento y guías
├── evidence/             # Capturas de telemetría, alertas y pruebas de contención
├── playbooks/            # Procedimientos operativos estándar (SOPs) de respuesta a incidentes
├── scripts/              # Scripts de automatización y soporte de hipervisor
└── README.md
```

---

## Topología de Red

El laboratorio está desplegado en VirtualBox utilizando un esquema de dos interfaces de red por máquina:

- **Adaptador 1 (NAT):** Acceso a internet para descargas de paquetes y actualizaciones.
- **Adaptador 2 (Host-Only `vboxnet0`):** Subred privada `192.168.56.0/24` para el tráfico de ataque, telemetría e ingesta de logs.

```
                          HOST UBUNTU (192.168.56.1)
             +---------------------------------------------------+
             | Control central, navegador de gestión e hipervisor|
             +-------------------------+-------------------------+
                                       | Subred vboxnet0 (192.168.56.0/24)
         +-----------------------------+-----------------------------+
         |                             |                             |
         v                             v                             v
+------------------+         +-------------------+         +-------------------+
|  Red Team (Kali) |         |  Víctima Windows  |         |  Víctima Linux    |
|  192.168.56.20   |         |  192.168.56.10    |         |  192.168.56.15    |
|  Hydra, Nmap     |         |  Windows 11 Pro   |         |  Ubuntu Server    |
|  Atomic Red Team |         |  Sysmon + Scripts |         |  OpenSSH, Web App |
+--------+---------+         +---------+---------+         +---------+---------+
         |                             |                             |
         | Ataques                     | Logs / Telemetría           | Logs SSH / Systemd
         |                             v                             v
         |                   +-------------------------------------------------+
         +------------------>|               Wazuh SIEM / EDR                  |
                             |               192.168.56.30                     |
                             | Indexer (OpenSearch) + Manager + Web Dashboard  |
                             +-------------------------------------------------+
```

| Nodo | Sistema Operativo | IP Lab (`vboxnet0`) | Función |
| :--- | :--- | :--- | :--- |
| **SOC SIEM** | Ubuntu Server | `192.168.56.30` | Ingesta de logs, correlación de eventos y Active Response |
| **Endpoint Windows** | Windows 11 Pro | `192.168.56.10` | Telemetría con Microsoft Sysmon y PowerShell ScriptBlock Logging |
| **Servidor Linux** | Ubuntu Server | `192.168.56.15` | Servicios SSH y aplicaciones web para emulación de intrusiones |
| **Atacante** | Kali Linux | `192.168.56.20` | Emulación de adversarios y pruebas controladas de seguridad |

---

## Estado de los Casos de Estudio

### Infraestructura Base
- [x] Hipervisor configurado con red aislada `192.168.56.0/24` y sincronización NTP unificada.
- [x] Servidor Wazuh 4.9 All-in-One operativo con Dashboard web HTTPS.
- [x] Agentes Wazuh conectados y reportando en estado activo (Windows 11 y Ubuntu Server).
- [x] Telemetría avanzada instrumentada: Sysmon en Windows y auditoría de journald en Linux.

### Caso de Estudio 1: Fuerza Bruta SSH (MITRE ATT&CK T1110.001)
- [x] Reconocimiento de servicios expuestos con Nmap (`evidence/T1110_Password_Spraying/00_nmap_reconnaissance.png`).
- [x] Emulación ofensiva con Hydra desde Kali contra el puerto 22 (`evidence/T1110_Password_Spraying/01_hydra_attack_kali.png`).
- [x] Identificación de brecha de visibilidad en Linux moderno: el nuevo proceso `sshd-session` no disparaba la regla legacy de Wazuh.
- [x] Desarrollo de regla de detección Sigma neutral ([`lnx_sshd_session_brute_force.yml`](detections/sigma/linux/lnx_sshd_session_brute_force.yml)).
- [x] Regla personalizada de correlación en Wazuh XML (Regla 100010, Nivel 10) validada en el panel (`evidence/T1110_Password_Spraying/02_wazuh_custom_rule_100010.png` y `03_wazuh_level10_dashboard.png`).
- [x] Playbook de respuesta a incidentes bajo estándar NIST/SANS ([`PB-01_BruteForce_SSH.md`](playbooks/PB-01_BruteForce_SSH.md)).
- [x] Contención automatizada con Active Response: bloqueo de IP en `iptables` de la víctima comprobado en tiempo real (`evidence/T1110_Password_Spraying/04_active_response_containment.png` y `05_iptables_firewall_drop.png`).

### Caso de Estudio 2: Credential Dumping en Windows (MITRE ATT&CK T1003.001)
- [ ] Volcado de memoria del proceso `lsass.exe` con herramientas ofensivas controladas.
- [ ] Análisis de telemetría Sysmon Event ID 10 (`ProcessAccess`) y correlación en el SIEM.
- [ ] Regla de detección Sigma y playbook de respuesta.

---

Para más detalles sobre la configuración técnica y los procedimientos, consultar la [Base de Conocimiento](docs/BASE_DE_CONOCIMIENTO.md) y el [Estado del Proyecto](docs/ESTADO_DEL_PROYECTO.md).
