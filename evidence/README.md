# 📸 Repositorio de Evidencias Forenses & Telemetría

Este directorio almacena las capturas de pantalla, fragmentos de logs JSON y registros generados durante las sesiones de prueba.

---

## 📁 Estructura Recomendada por Caso de Estudio

Para cada caso de estudio (ej: `T1110_Password_Spraying` o `T1003_LSASS_Dumping`):

```
evidence/
└── T1110_Password_Spraying/
    ├── 01_red_execution.png          # Captura de la terminal de Kali ejecutando Hydra/Atomics
    ├── 02_sysmon_raw_event.json      # Evento crudo exportado de Sysmon / Visor de eventos
    ├── 03_wazuh_alert_dashboard.png  # Alerta visualizada en el Dashboard web del SIEM
    └── 04_active_response_log.png    # Evidencia del bloqueo de la IP atacante
```

> [!TIP]
> Las 4 capturas clave por caso corresponden a la plantilla de publicación técnica de LinkedIn documentada en [`docs/Guia_Plantillas_LinkedIn.docx`](file:///home/anfrimax/Desktop/purple-team-soc-lab/docs/Guia_Plantillas_LinkedIn.docx).
