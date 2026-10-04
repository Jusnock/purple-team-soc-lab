# 📘 SOC Playbook: Respuesta a Incidentes - Fuerza Bruta SSH (MITRE ATT&CK T1110.001)

> **ID del Playbook:** `PB-01_BruteForce_SSH`  
> **Versión:** 1.0  
> **Severidad de Alerta:** Alta (Nivel 10)  
> **Técnicas MITRE ATT&CK:**  
> - **T1110.001** (*Credential Access: Password Guessing*)  
> - **T1021.004** (*Lateral Movement: SSH*)  
> **Fuentes de Telemetría:** Linux Syslog, `systemd-journald`, OpenSSH (`sshd-session`), Wazuh SIEM/EDR  

---

## 1. 🎯 Propósito y Alcance

Este procedimiento operativo estándar (SOP) define las acciones requeridas por el analista del SOC (Tier 1 / Tier 2) ante la detección de múltiples intentos fallidos de autenticación SSH dirigidos contra un servidor Linux de la infraestructura corporativa.

---

## 2. 🚨 Criterios de Disparo y Reglas SIEM

| Regla ID | Nivel | Descripción | Acción Requerida |
| :---: | :---: | :--- | :--- |
| **5760** | 5 (Medium) | `sshd: authentication failed.` (Fallo individual en `sshd-session`) | Monitoreo pasivo (línea base). |
| **5503** | 5 (Medium) | `PAM: User login failed.` | Monitoreo pasivo. |
| **100010** | **10 (High)** | **`sshd-session: Ataque de fuerza bruta detectado desde la misma IP`** ($\ge 5$ fallos en 60s) | **Activación inmediata de este Playbook.** |

---

## 3. 🔄 Flujo de Respuesta (Marco SANS / NIST SP 800-61)

```
[1. DETECCIÓN / TRIAGE]
         │
         ▼
¿Hubo algún login exitoso (Regla 5715) desde esa IP?
       ├── SÍ ──> ⚠️ ESCALAR A INCIDENTE CRÍTICO (Compromiso de cuenta / Acceso inicial)
       └── NO ──> [2. CONTENCIÓN]
                        │
                        ▼
                 Bloqueo de IP atacante (Active Response / iptables)
                        │
                        ▼
                 [3. ERRADICACIÓN Y REMEDIACIÓN]
                        │
                        ▼
                 Hardening de SSH (Deshabilitar passwords, fail2ban)
                        │
                        ▼
                 [4. LECCIONES APRENDIDAS]
```

---

## 4. 🔍 Procedimiento de Triage e Investigación (Tier 1)

1. **Identificar los metadatos del evento en el SIEM:**
   - **IP Atacante (`data.srcip`):** Determinar si es interna (`192.168.56.0/24`) o externa (Internet).
   - **Usuario Objetivo (`data.dstuser`):** Identificar si la cuenta atacada es privilegiada (`root`, `admin`) o de usuario estándar (`osboxes`).
   - **Volumen y Frecuencia:** Verificar el número de intentos por segundo (`firedtimes` y gráfico temporal).

2. **Verificar si el atacante logró entrar (Condición Crítica):**
   - En Wazuh **Discover**, buscar:
     ```text
     data.srcip: "<IP_ATACANTE>" and rule.id: 5715
     ```
   - *Si la Regla 5715 ("SSHD: authentication succeeded") existe inmediatamente posterior a la ráfaga de fallos, asumir compromiso de cuenta y saltar a contención de host.*

---

## 5. 🛑 Contención (Tier 2 / Active Response)

### A. Contención Automatizada (Active Response en Wazuh)
Si la respuesta activa está habilitada en `/var/ossec/etc/ossec.conf`:
- El comando `firewall-drop` añade automáticamente una regla de bloqueo en `iptables`/`nftables` contra `data.srcip` durante 10 minutos (600s).

### B. Contención Manual Inmediata (Terminal del Host Víctima)
Si se requiere bloqueo perimetral manual inmediato:
```bash
# Bloquear la IP atacante en la cadena INPUT de iptables
sudo iptables -I INPUT -s 192.168.56.20 -j DROP

# Verificar que la regla esté activa
sudo iptables -L INPUT -v -n
```

---

## 6. 🧹 Erradicación y Hardening (Post-Incidente)

Para mitigar permanentemente este vector de ataque en servidores productivos:

1. **Deshabilitar la autenticación por contraseña en SSH (Recomendado):**
   En `/etc/ssh/sshd_config` o `/etc/ssh/sshd_config.d/`:
   ```text
   PasswordAuthentication no
   PubkeyAuthentication yes
   PermitRootLogin no
   ```
2. **Reducir el umbral de reintentos por conexión:**
   ```text
   MaxAuthTries 3
   LoginGraceTime 30
   ```
3. **Reiniciar el servicio SSH:**
   ```bash
   sudo systemctl restart ssh
   ```

---

## 7. 📝 Registro y Cierre del Caso
- Documentar IP de origen, timestamps, técnica ATT&CK `T1110.001`.
- Adjuntar capturas de pantalla de la telemetría en el repositorio de evidencias (`evidence/T1110_Password_Spraying/`).
- Marcar la alerta en el SIEM como **Resuelta (True Positive - Closed)**.
