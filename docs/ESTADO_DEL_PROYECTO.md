# 🟣 Estado Actual del Proyecto y Contexto del Laboratorio
> **SOC & Purple Team Enterprise Simulation Lab**
> *Última actualización: 04 de Octubre, 2026 (Sesión 4)*

---

## 1. 🖥️ Especificaciones de Hardware del Host

* **Procesador:** Intel Core Ultra 7 165H (Arquitectura híbrida de 22 hilos multi-core)
* **Memoria RAM:** 32 GB RAM DDR5 (>25 GB libres para virtualización; verificado soporte de las 4 VMs concurrentes con ~10 GB libres de margen)
* **Almacenamiento:** SSD NVMe de alta velocidad (>250 GB libres)
* **Sistema Operativo Host:** Ubuntu 26.04.1 LTS con Kernel Linux 7.0.0-31-generic
* **Hipervisor:** VirtualBox 7.2.6 (Módulos `vboxdrv`, `vboxnetadp`, `vboxnetflt` parcheados y compilados con éxito para Kernel 7.0+)
* **Script de parcheo del Kernel:** [`scripts/patch_vbox_kernel7.sh`](file:///home/anfrimax/Desktop/purple-team-soc-lab/scripts/patch_vbox_kernel7.sh)

---

## 2. 🗺️ Topología de Red y Nodos del Laboratorio (100% Homologada)

El laboratorio opera bajo un **Esquema de Doble Adaptador (Dual-NIC)** para balancear aislamiento de seguridad y comodidad de administración:
* **Adaptador 1 (NAT):** Salida a internet para descargas, sincronización de hora (NTP) y actualizaciones de paquetes sin exponer las VMs a la red externa.
* **Adaptador 2 (Host-Only `vboxnet0`):** Red privada y aislada del laboratorio (`192.168.56.0/24`) para el tráfico de ataques, telemetría e ingesta de logs.

| Nodo / VM | IP Lab (`vboxnet0`) | Estado de Conexión | Recursos (RAM / vCPU) | Rol y Componentes Instalados |
| :--- | :--- | :--- | :--- | :--- |
| **Host Ubuntu** | `192.168.56.1` | Nativo (UP) | 32 GB Host | Gateway del lab, navegador de acceso al Dashboard SOC y control central |
| **Ubuntu Server Wazuh** | `192.168.56.30` | **Activo / Operativo** | 6 GB RAM / 4 vCPU | **Blue Team SOC:** Wazuh All-in-One 4.9.x (Indexer + Manager + Dashboard HTTPS + API 55000) |
| **Windows 11 Pro** | `192.168.56.10` | **Agente 001 Activo** | 6 GB RAM / 4 vCPU | **Víctima Windows:** Sysmon (SwiftOnSecurity), PowerShell Script Block Logging, Wazuh Agent 4.9.2 |
| **Ubuntu Server** | `192.168.56.15` | **Agente 002 Activo** | 4 GB RAM / 4 vCPU | **Víctima Linux:** OWASP Juice Shop (3000), SSH (22), Wazuh Agent 4.9.2 (`ubuntu-victim`) |
| **Kali Linux** | `192.168.56.20` | **Activo / Configurado** | 4 GB RAM / 7 vCPU | **Red Team (Atacante):** Atomic Red Team, Hydra, Nmap, NetExec, Python |

---

## 3. ✅ Hitos Completados Hasta el Momento

1. **Compatibilidad del Hipervisor en Linux 7.0:**
   - Diagnóstico y resolución de restricción de símbolos del kernel Linux 7.0 (`cr4_update_irqsoff` y `__flush_tlb_all`).
   - Módulos de VirtualBox parcheados y cargados exitosamente con [`scripts/patch_vbox_kernel7.sh`](file:///home/anfrimax/Desktop/purple-team-soc-lab/scripts/patch_vbox_kernel7.sh).

2. **Aprovisionamiento e Instrumentación de la Víctima Windows 11 Pro:**
   - VM creada con UEFI/EFI64, TPM 2.0 emulado y Guest Additions.
   - Instalación del controlador y servicio de **Microsoft Sysmon64** con esquema de detección de amenazas de **SwiftOnSecurity** (`sysmonconfig.xml`).
   - Enrolamiento de agente oficial Wazuh 4.9.2 en estado **`Active`** (Agente ID: `001`, Nombre: `DESKTOP-TS224KA`).
   - IP estática fijada en `192.168.56.10`.

3. **Despliegue y Puesta en Marcha de Wazuh SIEM Server:**
   - VM dedicada `Ubuntu Server Wazuh` desplegada con Wazuh All-in-One 4.9.x.
   - Interfaz Host-Only configurada con IP fija `192.168.56.30`.
   - Servicios activos y verificados: **Wazuh Indexer (OpenSearch)**, **Wazuh Manager**, **Wazuh Dashboard** y **Filebeat**.
   - Puertos operativos en el lab: `443` (Dashboard HTTPS), `1514` (Ingesta de eventos), `1515` (Registro de agentes authd), `55000` (API REST).
   - Acceso exitoso verificado al panel web desde el navegador del Host en `https://192.168.56.30`.

4. **Integración y Enrolamiento de la Víctima Linux (`Ubuntu Server`):**
   - Habilitado el segundo adaptador en NAT (`nic2="nat"`), completando la arquitectura Dual-NIC del nodo.
   - IP estática configurada en Netplan: `192.168.56.15`.
   - Distribución e instalación de `wazuh-agent_4.9.2-1_amd64.deb`.
   - Enrolamiento exitoso autenticado mediante `agent-auth -m 192.168.56.30 -A ubuntu-victim`.
   - Agente registrado y visible en el Dashboard de Wazuh con estado **`Active`** (Agente ID: `002`, Nombre: `ubuntu-victim`).
   - Servicios verificados: SSH (`22/TCP`) y OWASP Juice Shop (`3000/TCP`).

5. **Puesta a Punto del Atacante (`Kali Linux`):**
   - Interfaz Host-Only `eth1` configurada con IP estática `192.168.56.20/24` (sin gateway redundante para preservar salida a internet por NAT `eth0`).
   - Conectividad de red de malla completa verificada (ping cruzado con 0% de pérdida hacia el Host, Wazuh, Windows y Ubuntu).

6. **Sincronización Horaria y Timezone Unificado (NTP):**
   - Diagnóstico de desfase temporal: detección de reloj atrasado en VMs por snapshots antiguos y zona horaria en UTC.
   - Configuración de zona horaria unificada `America/Argentina/Buenos_Aires` (UTC-3) en todos los nodos Linux.
   - Activación de sincronización automática por internet mediante `systemd-timesyncd` (`timedatectl set-ntp true`) para garantizar que todas las alertas SIEM caigan en el segundo exacto.

7. **Reconocimiento de Red y Descubrimiento de Servicios (MITRE ATT&CK T1046 - Fase Pre-Ataque):**
   - Emulación ofensiva ejecutada desde Kali Linux (`192.168.56.20`) hacia la víctima Linux (`192.168.56.15`).
   - Comando ejecutado:
     ```bash
     nmap -sV -Pn -p 22,80,3000,8080 192.168.56.15
     ```
     *(Decisión táctica documentada: Se descartó intencionalmente el uso de scripts por defecto `-sC` para evitar sobrecarga de información y mantener un footprint de reconocimiento limpio y enfocado exclusivamente en versiones y puertos).*
   - **Resultados del escaneo:**
     * `22/tcp   open     ssh          OpenSSH 9.9p1 Ubuntu 3ubuntu3.2 (protocol 2.0)` -> Superficie de ataque elegida para la intrusión por fuerza bruta.
     * `80/tcp   filtered http`
     * `3000/tcp open     ppp?` (Node.js / OWASP Juice Shop)
     * `8080/tcp filtered http-proxy`
   - **Evidencia guardada:** Captura guardada en [`evidence/T1110_Password_Spraying/00_nmap_reconnaissance.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/00_nmap_reconnaissance.png).

8. **Emulación Ofensiva & Fuerza Bruta SSH (MITRE ATT&CK T1110.001 - Red Team):**
   - Ejecución exitosa de ataque de fuerza bruta con Hydra desde Kali Linux (`192.168.56.20`) iterando contraseñas contra el servicio SSH en `192.168.56.15:22`.
   - **Evidencia archivada:** [`evidence/T1110_Password_Spraying/01_hydra_attack_kali.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/01_hydra_attack_kali.png).

9. **Telemetría Profunda e Ingesta SIEM (Blue Team):**
   - Ingesta en tiempo real desde `systemd-journald` de la víctima hacia el indexer de Wazuh.
   - Diagnóstico técnico de arquitectura moderna OpenSSH: identificación de la migración de logs desde el proceso legacy `sshd` hacia `sshd-session` (OpenSSH 9.9p1).
   - Generación exitosa de eventos de autenticación fallida: **Regla 5760** (*"sshd: authentication failed"* - Nivel 5) y **Regla 5503** (*"PAM: User login failed"* - Nivel 5).
   - Disparo y validación de alertas críticas correlacionadas: **Regla 5763 / Regla personalizada 100010 (Nivel 10)** (*"sshd-session: Ataque de fuerza bruta detectado desde la misma IP"*).
   - **Evidencias archivadas:**
     * [`evidence/T1110_Password_Spraying/02_wazuh_custom_rule_100010.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/02_wazuh_custom_rule_100010.png) (Detalle forense de telemetría expandida con MITRE T1110.001).
     * [`evidence/T1110_Password_Spraying/03_wazuh_level10_dashboard.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/03_wazuh_level10_dashboard.png) (Dashboard filtrado en Nivel 10 mostrando la alerta 100010).

10. **Detection Engineering & Detection-as-Code (Purple Team):**
    - Redacción y versionado de regla neutral en formato estándar **Sigma (YAML)**: [`detections/sigma/linux/lnx_sshd_session_brute_force.yml`](file:///home/anfrimax/Desktop/purple-team-soc-lab/detections/sigma/linux/lnx_sshd_session_brute_force.yml).
    - Creación e implementación de regla XML nativa para Wazuh Manager: [`detections/wazuh/local_rules.xml`](file:///home/anfrimax/Desktop/purple-team-soc-lab/detections/wazuh/local_rules.xml) (Regla personalizada `100010`).
    - Elaboración del Playbook oficial de Respuesta a Incidentes (SOC SOP): [`playbooks/PB-01_BruteForce_SSH.md`](file:///home/anfrimax/Desktop/purple-team-soc-lab/playbooks/PB-01_BruteForce_SSH.md) bajo estándares NIST SP 800-61 / SANS.

11. **Mitigación Defensiva & Active Response (SOAR / Contención Automatizada):**
    - Configuración del módulo `<active-response>` en `ossec.conf` con el comando `firewall-drop` asociado a la regla de fuerza bruta.
    - Validación empírica: en el instante del ataque, el agente en `ubuntu-victim` inyectó una regla `DROP` en `iptables` contra la IP `192.168.56.20`.
    - Bloqueo perimetral verificado: Kali perdió conectividad de inmediato y los paquetes SSH fueron descartados.
    - **Evidencias archivadas:**
      * [`evidence/T1110_Password_Spraying/04_active_response_containment.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/04_active_response_containment.png) (Conexión SSH congelada desde Kali).
      * [`evidence/T1110_Password_Spraying/05_iptables_firewall_drop.png`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/05_iptables_firewall_drop.png) (Regla activa en `iptables` de la víctima con paquetes dropeados).

---

## 4. 🚀 Hoja de Ruta para la Siguiente Sesión (Ejecución Inmediata)

1. **Publicación y Write-Up del Caso de Estudio 1 (LinkedIn / GitHub):**
   - Publicar el post profesional con las 5 evidencias gráficas de la carpeta [`evidence/T1110_Password_Spraying/`](file:///home/anfrimax/Desktop/purple-team-soc-lab/evidence/T1110_Password_Spraying/).

2. **Caso de Estudio 2 (Windows Endpoint Security & Credential Access):**
   - Emulación de MITRE ATT&CK **T1003.001** (Dump de memoria LSASS con Mimikatz / ProcDump / `comsvcs.dll`) en Windows 11.
   - Validación de telemetría **Microsoft Sysmon Event ID 10** (`ProcessAccess` con `0x1010` / `0x1F0FFF`).
   - Desarrollo de regla de detección Sigma y Playbook de respuesta PB-02.
