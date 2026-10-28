/*
 * Modelo legible de observaciones estáticas del arranque GBA.
 * NO es el ensamblador original ni una implementación completa del juego.
 */
#include <stdint.h>

#define LZC_ROM_BASE              UINT32_C(0x08000000)
#define LZC_IRQ_VECTOR_SLOT       UINT32_C(0x03007FFC)
#define LZC_IRQ_HANDLER_ENTRY     UINT32_C(0x08000104)
#define LZC_GAME_LOOP_THUMB_PTR   UINT32_C(0x08000231)
#define LZC_MAIN_MODE_RAM         UINT32_C(0x03000BDE)
#define LZC_DISPATCH_MODE_MAX     14u

typedef struct {
    uint32_t irq_stack_top;
    uint32_t system_stack_top;
    uint32_t irq_vector_slot;
    uint32_t irq_handler_entry;
    uint32_t thumb_entry_pointer;
    uint32_t main_mode_address;
    uint32_t dispatch_mode_max;
} lzc_boot_observation_t;

const lzc_boot_observation_t lzc_boot_observed = {
    UINT32_C(0x03007FA0),
    UINT32_C(0x03007E60),
    LZC_IRQ_VECTOR_SLOT,
    LZC_IRQ_HANDLER_ENTRY,
    LZC_GAME_LOOP_THUMB_PTR,
    LZC_MAIN_MODE_RAM,
    LZC_DISPATCH_MODE_MAX
};

/*
 * Static interpretation:
 * - The entry at file offset 0x000 branches to bus address 0x080000C0.
 * - The reset/bootstrap code changes CPU mode and loads the IRQ/System stacks.
 * - It stores the IRQ handler address at 0x03007FFC.
 * - BX through 0x08000231 switches into Thumb at ROM offset 0x230.
 * - The Thumb main loop reads the mode from 0x03000BDE and dispatches by table.
 *
 * Keep this file as descriptive data. It intentionally does not write memory or
 * pretend to emulate the real game. Confirm each instruction in Ghidra ARMv4T.
 */
