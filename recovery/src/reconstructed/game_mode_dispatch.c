#include <stddef.h>
#include "game_mode_dispatch.h"

/*
 * Target addresses read from the 15-word dispatch table at ROM file offset
 * 0x278 and cross-checked with the named game-mode ordering in the reference
 * source. Handler behavior is not implemented in this table.
 */
static const uint32_t kObservedHandlerTargets[LZC_MODE_COUNT] = {
    0x080002B4u, /*  0: title */
    0x08000448u, /*  1: in game */
    0x08000548u, /*  2: soft reset */
    0x080004D0u, /*  3: map screen */
    0x0800054Eu, /*  4: cutscene */
    0x080005D0u, /*  5: SA-X close-up */
    0x080005E4u, /*  6: erase SRAM menu */
    0x080003ACu, /*  7: file select/new file intro */
    0x08000624u, /*  8: game over */
    0x0800069Cu, /*  9: ending */
    0x080006B0u, /* 10: SR388 collision death */
    0x080006D0u, /* 11: credits */
    0x080006E4u, /* 12: demo */
    0x08000730u, /* 13: unresolved mode */
    0x0800074Cu  /* 14: debug */
};

bool lzc_lookup_observed_mode_target(int16_t mode, uint32_t *rom_address_out)
{
    if (rom_address_out == NULL || mode < 0 || mode >= LZC_MODE_COUNT)
        return false;

    *rom_address_out = kObservedHandlerTargets[(uint16_t)mode];
    return true;
}
