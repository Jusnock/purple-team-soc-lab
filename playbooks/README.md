# 📋 Playbooks de Respuesta a Incidentes (SOC SOPs)

Este directorio contiene los procedimientos operativos estándar (SOPs) y flujos de trabajo para la contención, erradicación y recuperación ante incidentes de seguridad detectados por el SIEM.

---

## 🗂️ Playbooks Disponibles / Planificados

| Playbook | Técnica MITRE | Vector de Ataque | Acciones de Respuesta |
| :--- | :--- | :--- | :--- |
| **PB-01_BruteForce_SSH.md** | `T1110.001` / `T1110.003` | Fuerza bruta y password spraying | Bloqueo perimetral en firewall / iptables mediante Active Response |
| **PB-02_Credential_Dumping.md** | `T1003.001` | Acceso a memoria de `lsass.exe` | Aislamiento de red del endpoint, terminación de proceso atacante |
| **PB-03_Web_Vulnerability.md** | `T1190` | Explotación web contra Juice Shop | Bloqueo de IP de origen, rotación de credenciales comprometidas |
