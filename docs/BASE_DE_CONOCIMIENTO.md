# 📚 Base de Conocimiento y Runbook Técnico
> **SOC Operations, Detection Engineering & Purple Team Simulation Lab**
> *Manual de referencia rápida de herramientas, sintaxis de comandos, telemetría y procedimientos tácticos.*

---

## 📑 Tabla de Contenidos
1. [🔵 Telemetría de Endpoints (Blue Team & Sensores)](#1--telemetría-de-endpoints-blue-team--sensores)
   - [Microsoft Sysmon (Windows)](#microsoft-sysmon-windows)
   - [PowerShell Script Block Logging](#powershell-script-block-logging)
   - [Linux Auditd (Auditoría del Kernel)](#linux-auditd-auditoría-del-kernel)
2. [🟣 SIEM & Centro de Operaciones (Wazuh SIEM / EDR)](#2--siem--centro-de-operaciones-wazuh-siem--edr)
   - [Arquitectura y Componentes](#arquitectura-y-componentes)
   - [Comandos de Control y Verificación](#comandos-de-control-y-verificación)
   - [Agentes Wazuh (Enrolamiento y Gestión)](#agentes-wazuh-enrolamiento-y-gestión)
   - [Motor de Detección: Reglas y wazuh-logtest](#motor-de-detección-reglas-y-wazuh-logtest)
3. [⚔️ Emulación de Adversarios (Red Team & TTPs)](#3-️-emulación-de-adversarios-red-team--ttps)
   - [Atomic Red Team (MITRE ATT&CK)](#atomic-red-team-mitre-attck)
   - [Hydra (Fuerza Bruta & Password Spraying)](#hydra-fuerza-bruta--password-spraying)
   - [Nmap (Reconocimiento & Detección de Vulnerabilidades)](#nmap-reconocimiento--detección-de-vulnerabilidades)
4. [🛡️ Detection-as-Code & Formato Sigma](#4-️-detection-as-code--formato-sigma)
   - [Estructura y Anatomía de una Regla Sigma](#estructura-y-anatomía-de-una-regla-sigma)
   - [Ejemplo Real: Detección de LSASS Dumping (T1003.001)](#ejemplo-real-detección-de-lsass-dumping-t1003001)
5. [⚙️ Redes y Administración del Hipervisor](#5-️-redes-y-administración-del-hipervisor)
   - [VBoxManage (VirtualBox CLI)](#vboxmanage-virtualbox-cli)
   - [Configuración de Red Estática (Linux Netplan & Windows netsh)](#configuración-de-red-estática-linux-netplan--windows-netsh)

---

## 1. 🔵 Telemetría de Endpoints (Blue Team & Sensores)

### Microsoft Sysmon (Windows)
**System Monitor (Sysmon)** es un controlador de dispositivo de Windows (`SysmonDrv.sys`) y un servicio que permanece residente tras los reinicios para monitorizar y registrar la actividad del sistema en el registro de eventos de Windows (`Microsoft-Windows-Sysmon/Operational`).

#### Comandos Esenciales de Sysmon:
```powershell
# Instalar Sysmon por primera vez aceptando el EULA y aplicando una configuración XML
.\Sysmon64.exe -accepteula -i sysmonconfig.xml

# Actualizar la configuración activa en caliente (sin reiniciar el servicio)
.\Sysmon64.exe -c sysmonconfig_updated.xml

# Comprobar la versión instalada y el esquema de configuración cargado
.\Sysmon64.exe -s

# Desinstalar completamente el servicio y el controlador del kernel
.\Sysmon64.exe -u
```

#### Catálogo de Event IDs de Sysmon Críticos para Detección:
| Event ID | Nombre del Evento | Campos Clave de Telemetría | Valor para Detección de Amenazas |
| :---: | :--- | :--- | :--- |
| **1** | **Process Creation** | `Image`, `CommandLine`, `ParentImage`, `ParentCommandLine`, `User`, `Hashes` | Detección de procesos anómalos, scripts sospechosos y árboles de procesos maliciosos (ej: `winword.exe` spawning `powershell.exe`). |
| **3** | **Network Connection** | `SourceIp`, `DestinationIp`, `DestinationPort`, `Image`, `Protocol` | Tráfico saliente a servidores de Comando y Control (C2), conexiones SMB/RDP laterales. |
| **7** | **Image Loaded (DLL)** | `ImageLoaded`, `Hashes`, `Signed`, `SignatureStatus` | Carga de bibliotecas DLL sin firmar, ataques de DLL Sideloading y DLL Injection. |
| **8** | **CreateRemoteThread** | `SourceImage`, `TargetImage`, `StartAddress` | Detección de inyección de código en procesos legítimos (ej: inyectar shellcode en `explorer.exe`). |
| **10** | **ProcessAccess** | `SourceImage`, `TargetImage`, `GrantedAccess`, `CallTrace` | **El evento más crítico:** detecta programas accediendo a la memoria de `lsass.exe` para volcado de credenciales con accesos `0x1010` o `0x1F0FFF`. |
| **11** | **FileCreate** | `TargetFilename`, `CreationUtcTime`, `Image` | Detección de creación de binarios maliciosos en `\AppData\`, `\Temp\` o scripts de persistencia. |
| **12 / 13** | **RegistryEvent** | `EventType`, `TargetObject`, `Details` | Modificaciones en claves de persistencia de Windows (`HKLM\...\Run`, `RunOnce`, servicios). |
| **22** | **DNSEvent** | `QueryName`, `QueryResults`, `Image` | Resoluciones de dominios sospechosos, túneles DNS y algoritmos de generación de dominios (DGA). |

---

### PowerShell Script Block Logging
Registra el contenido completo del código ejecutado en PowerShell, independientemente de si proviene de un archivo `.ps1`, de un comando interactivo o de código ofuscado/descargado en memoria (ataques *fileless*).

#### Activación vía Registro de Windows (PowerShell Administrador):
```powershell
# Habilitar Script Block Logging global
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name "EnableScriptBlockLogging" -Value 1 -Type DWord
```

#### Consulta de Eventos de Script Block en Consola:
* **Ruta del log:** `Microsoft-Windows-PowerShell/Operational`
* **Event ID:** **`4104`** (Script Block Logging)
```powershell
# Obtener los últimos 3 bloques de código ejecutados en el sistema
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational'; Id=4104} -MaxEvents 3 | 
    Format-List TimeCreated, Message
```

---

### Linux Auditd (Auditoría del Kernel)
El daemon `auditd` es el sistema nativo de auditoría de Linux que intercepta llamadas al sistema (*syscalls*) para rastrear comandos ejecutados y modificaciones de archivos sensibles.

#### Comandos de Gestión y Reglas (`auditctl`):
```bash
# Verificar estado del servicio de auditoría
sudo systemctl status auditd

# Monitorear escrituras en /etc/passwd con una etiqueta identificativa (-k identity_changes)
sudo auditctl -w /etc/passwd -p wa -k identity_changes

# Auditar todas las ejecuciones de comandos de 64 bits (syscall execve)
sudo auditctl -a always,exit -F arch=b64 -S execve -k exec_monitor

# Listar todas las reglas actualmente cargadas en el kernel
sudo auditctl -l
```

#### Análisis y Búsqueda de Eventos Forenses (`ausearch` y `aureport`):
```bash
# Buscar eventos con la clave 'identity_changes' ocurridos hoy
sudo ausearch -k identity_changes -ts today

# Generar un resumen estadístico de todos los comandos ejecutados en el sistema
sudo aureport -x --summary
```

---

## 2. 🟣 SIEM & Centro de Operaciones (Wazuh SIEM / EDR)

### Arquitectura y Componentes
Wazuh es una plataforma integral de seguridad open-source basada en tres piezas centrales:
1. **Wazuh Indexer:** Motor de almacenamiento y búsqueda en tiempo real basado en OpenSearch.
2. **Wazuh Server (Manager):** Motor de análisis y correlación de logs, decodificadores y reglas de alerta.
3. **Wazuh Dashboard:** Interfaz web para visualización gráfica de incidentes, compliance e inventario.
4. **Wazuh Agent:** Agente ligero multiplataforma (Windows, Linux, macOS) que recopila y transmite eventos al Server mediante un canal TLS cifrado (puerto `1514/TCP`).

---

### Comandos de Control y Verificación
En la máquina **`Ubuntu Server Wazuh`**:
```bash
# Comprobar el estado integral de todos los módulos del servidor Wazuh
sudo /var/ossec/bin/wazuh-control status

# Verificar servicios individuales en systemd
sudo systemctl status wazuh-manager
sudo systemctl status wazuh-indexer
sudo systemctl status wazuh-dashboard

# Monitorear las alertas generadas en tiempo real (JSON stream)
sudo tail -f /var/ossec/logs/alerts/alerts.json | jq .

# Ver el log operativo del gestor Wazuh (para depurar errores)
sudo tail -f /var/ossec/logs/ossec.log
```

---

### Agentes Wazuh (Enrolamiento y Gestión)

#### Comandos en el Manager (Servidor):
```bash
# Listar todos los agentes conectados y su estado (Active, Disconnected, Never connected)
sudo /var/ossec/bin/agent_control -l

# Ver detalles completos de un agente específico (ej: ID 001)
sudo /var/ossec/bin/agent_control -i 001
```

#### Instalación en Windows 11 (PowerShell Administrador):
```powershell
# Descargar el instalador MSI oficial
Invoke-WebRequest -Uri "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.9.2-1.msi" -OutFile "wazuh-agent.msi"

# Instalar y vincular automáticamente al servidor Wazuh (192.168.56.30)
msiexec.exe /i wazuh-agent.msi /q WAZUH_MANAGER='192.168.56.30' WAZUH_REGISTRATION_SERVER='192.168.56.30'

# Iniciar el servicio del agente
Start-Service Wazuh
```

#### Instalación en Ubuntu Server Víctima (Bash):
```bash
# Instalar el agente apuntando a la IP del Wazuh Server
sudo WAZUH_MANAGER='192.168.56.30' apt-get install wazuh-agent

# Habilitar e iniciar el servicio
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

---

### Motor de Detección: Reglas y `wazuh-logtest`
La herramienta **`wazuh-logtest`** es la utilidad más importante para los analistas e ingenieros de detección: permite pegar un evento de log en crudo y ver en vivo qué decodificador lo analiza, qué regla se dispara y qué nivel de alerta genera.

```bash
# Iniciar la herramienta de prueba de reglas
sudo /var/ossec/bin/wazuh-logtest
```
*(Al abrir, pegas una línea de log y Wazuh muestra la fase 1 de pre-decodificación, fase 2 de decodificación y fase 3 de coincidencia de reglas).*

---

## 3. ⚔️ Emulación de Adversarios (Red Team & TTPs)

### Atomic Red Team (MITRE ATT&CK)
**Atomic Red Team** es una librería de pruebas de ataque controladas y reproducibles, estructuradas según las técnicas de la matriz MITRE ATT&CK.

```powershell
# 1. Ver detalles de una técnica específica (ej: T1003.001 - Dump de memoria LSASS)
Invoke-AtomicTest T1003.001 -ShowDetails

# 2. Comprobar si el sistema cuenta con las herramientas necesarias para la prueba
Invoke-AtomicTest T1003.001 -CheckPrereqs

# 3. Descargar dependencias si falta algún binario
Invoke-AtomicTest T1003.001 -GetPrereqs

# 4. Ejecutar la prueba ofensiva controlada
Invoke-AtomicTest T1003.001 -TestNumbers 1

# 5. ¡CRUCIAL! Limpiar todos los archivos y rastros creados por la prueba
Invoke-AtomicTest T1003.001 -Cleanup
```

---

### Hydra (Fuerza Bruta & Password Spraying)
Herramienta de Kali Linux para emular ataques contra protocolos de autenticación en red (SSH, RDP, SMB, HTTP).

```bash
# Emulación de Fuerza Bruta SSH (MITRE T1110.001) contra Ubuntu Server
hydra -L usuarios.txt -P passwords.txt -t 4 -V ssh://192.168.56.15

# Emulación de Password Spraying (MITRE T1110.003): Probar UNA sola contraseña contra MUCHAS cuentas
# (Usa el parámetro -u para rotar la contraseña solo tras probar a todos los usuarios, evitando bloqueos)
hydra -L usuarios.txt -p "Password2026!" -u -t 2 ssh://192.168.56.15

# Ataque de autenticación contra el RDP de Windows 11
hydra -l analyst -P passwords.txt -t 1 rdp://192.168.56.10
```

---

### Nmap (Reconocimiento & Detección de Vulnerabilidades)
Herramienta estándar de exploración de red y mapeo de superficie de ataque.

```bash
# Descubrimiento de hosts activos en la subred del laboratorio (Ping sweep sin escanear puertos)
nmap -sn 192.168.56.0/24

# Escaneo sigiloso SYN (-sS) con detección de versiones (-sV) y detección de SO (-O)
nmap -sS -sV -O -p- -T4 192.168.56.10

# Ejecutar scripts de auditoría de vulnerabilidades conocidas (NSE Scripts) contra Juice Shop
nmap --script "vuln" -p 80,3000,22 192.168.56.15
```

---

## 4. 🛡️ Detection-as-Code & Formato Sigma

### Estructura y Anatomía de una Regla Sigma
Sigma es el estándar de la industria (en YAML) para describir reglas de detección de manera neutral e independiente del SIEM o tecnología subyacente.

```yaml
title: Suspicious LSASS Process Access via GrantedAccess
id: 5a7e1f4b-7a31-4c12-9def-123456789abc
status: production
description: Detecta intentos de apertura de proceso sobre lsass.exe con permisos típicos de volcado de memoria (Mimikatz / ProcDump).
references:
    - https://attack.mitre.org/techniques/T1003/001/
author: Purple Team SOC Lab
tags:
    - attack.credential_access
    - attack.t1003.001
logsource:
    category: process_access
    product: windows
detection:
    selection:
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess:
            - '0x1010'     # PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ
            - '0x1F0FFF'   # PROCESS_ALL_ACCESS
    filter:
        SourceImage|endswith:
            - '\svchost.exe'
            - '\MsMpEng.exe'  # Antivirus Windows Defender legítimo
    condition: selection and not filter
level: high
```

---

## 5. ⚙️ Redes y Administración del Hipervisor

### VBoxManage (VirtualBox CLI)
Gestión completa de máquinas virtuales desde la consola de comandos de tu Ubuntu host:

```bash
# Listar todas las VMs registradas
VBoxManage list vms

# Listar únicamente las VMs encendidas actualmente
VBoxManage list runningvms

# Apagar una VM de forma limpia mediante ACPI (equivalente a botón de apagado)
VBoxManage controlvm "Windows 11" acpipowerbutton

# Crear una instantánea (Snapshot) del estado actual de la VM
VBoxManage snapshot "Windows 11" take "Pre-Ataque_Limpio"

# Restaurar una instantánea previa
VBoxManage snapshot "Windows 11" restore "Pre-Ataque_Limpio"
```

---

### Configuración de Red Estática

#### En Windows 11 (CMD o PowerShell Administrador):
```cmd
:: Asignar IP fija al Adaptador 2 (Host-Only vboxnet0)
netsh interface ipv4 set address name="Ethernet 2" static 192.168.56.10 255.255.255.0 192.168.56.1
```

#### En Ubuntu Server (Netplan `/etc/netplan/01-netcfg.yaml`):
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:        # Adaptador 1 (NAT)
      dhcp4: true
    enp0s8:        # Adaptador 2 (Host-Only vboxnet0)
      dhcp4: false
      addresses:
        - 192.168.56.30/24
```
```bash
# Aplicar la configuración de red en Ubuntu
sudo netplan apply
```
