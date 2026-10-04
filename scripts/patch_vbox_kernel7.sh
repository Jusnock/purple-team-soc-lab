#!/bin/bash
set -e

echo "=== Aplicando parche de compatibilidad de VirtualBox para Kernel 7.0+ ==="

SRC_DIR="/usr/share/virtualbox/src/vboxhost"
SUPDRV_FILE="$SRC_DIR/vboxdrv/linux/SUPDrv-linux.c"
MEMOBJ_FILE="$SRC_DIR/vboxdrv/r0drv/linux/memobj-r0drv-linux.c"

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecuta este script con sudo: sudo bash $0"
  exit 1
fi

# 1. Asegurar backup de archivos originales
if [ ! -f "${SUPDRV_FILE}.orig" ]; then
    if [ -f "${SUPDRV_FILE}.bak" ]; then
        cp "${SUPDRV_FILE}.bak" "${SUPDRV_FILE}.orig"
    else
        cp "$SUPDRV_FILE" "${SUPDRV_FILE}.orig"
    fi
fi

if [ ! -f "${MEMOBJ_FILE}.orig" ]; then
    if [ -f "${MEMOBJ_FILE}.bak" ]; then
        cp "${MEMOBJ_FILE}.bak" "${MEMOBJ_FILE}.orig"
    else
        cp "$MEMOBJ_FILE" "${MEMOBJ_FILE}.orig"
    fi
fi

# Restaurar desde .orig limpio
cp "${SUPDRV_FILE}.orig" "$SUPDRV_FILE"
cp "${MEMOBJ_FILE}.orig" "$MEMOBJ_FILE"

# 2. Parchear SUPDrv-linux.c reemplazando supdrvOSChangeCR4 con inline assembly
python3 - << 'EOF'
import re

with open("/usr/share/virtualbox/src/vboxhost/vboxdrv/linux/SUPDrv-linux.c", "r") as f:
    content = f.read()

pattern = r"RTCCUINTREG VBOXCALL supdrvOSChangeCR4\(RTCCUINTREG fOrMask, RTCCUINTREG fAndMask\)[\s\S]*?#endif /\* RT_ARCH_AMD64 \|\| RT_ARCH_X86 \*/"

replacement = """RTCCUINTREG VBOXCALL supdrvOSChangeCR4(RTCCUINTREG fOrMask, RTCCUINTREG fAndMask)
{
    unsigned long fSavedFlags;
    local_irq_save(fSavedFlags);
    RTCCUINTREG const uOld = ASMGetCR4();
    RTCCUINTREG const uNew = (uOld & fAndMask) | fOrMask;
    if (uNew != uOld)
        ASMSetCR4(uNew);
    local_irq_restore(fSavedFlags);
    return uOld;
}
#endif /* RT_ARCH_AMD64 || RT_ARCH_X86 */"""

new_content, count = re.subn(pattern, replacement, content)
assert count == 1, f"Expected 1 replacement in SUPDrv-linux.c, got {count}"

with open("/usr/share/virtualbox/src/vboxhost/vboxdrv/linux/SUPDrv-linux.c", "w") as f:
    f.write(new_content)
print("SUPDrv-linux.c parcheado exitosamente (reemplazo de supdrvOSChangeCR4).")
EOF

# 3. Parchear memobj-r0drv-linux.c reemplazando __flush_tlb_all con recarga de CR3 en asm
python3 - << 'EOF'
with open("/usr/share/virtualbox/src/vboxhost/vboxdrv/r0drv/linux/memobj-r0drv-linux.c", "r") as f:
    content = f.read()

# Reemplazar la llamada a __flush_tlb_all()
new_content = content.replace('__flush_tlb_all();', '__asm__ __volatile__("movq %%cr3, %%rax; movq %%rax, %%cr3" : : : "rax", "memory");')

with open("/usr/share/virtualbox/src/vboxhost/vboxdrv/r0drv/linux/memobj-r0drv-linux.c", "w") as f:
    f.write(new_content)
print("memobj-r0drv-linux.c parcheado exitosamente (TLB flush).")
EOF

# 4. Reconstruir los módulos con vboxconfig
echo "Compilando e instalando módulos de kernel..."
/sbin/vboxconfig

echo "=== ¡Módulos de VirtualBox compilados e instalados exitosamente! ==="
