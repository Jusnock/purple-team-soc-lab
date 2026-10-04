# Reglas de Detección (Detection-as-Code)

Este directorio contiene las reglas de detección desarrolladas durante las emulaciones del laboratorio.

---

## Organización del Directorio

```
detections/
├── sigma/                    # Reglas en formato neutral Sigma (YAML)
│   ├── windows/              # Reglas para eventos de Sysmon y Security de Windows
│   └── linux/                # Reglas para Auditd y Syslog de Linux
└── wazuh/                    # Reglas nativas en XML para Wazuh Manager
    └── local_rules.xml       # Reglas personalizadas de correlación
```

---

## Estándar de Reglas Sigma
Cada regla debe mapear:
1. **Técnica MITRE ATT&CK:** Identificador oficial (ej. `attack.t1003.001`).
2. **Fuente de Datos (Logsource):** Categoría (`process_creation`, `process_access`, `network_connection`).
3. **Nivel de Severidad:** `low`, `medium`, `high`, `critical`.
4. **Filtros de Falsos Positivos:** Exclusiones explícitas de software legítimo (ej. antivirus, tareas del sistema).
