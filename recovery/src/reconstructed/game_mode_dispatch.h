#ifndef LZC_GAME_MODE_DISPATCH_H
#define LZC_GAME_MODE_DISPATCH_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    LZC_MODE_TITLE = 0,
    LZC_MODE_IN_GAME,
    LZC_MODE_SOFT_RESET,
    LZC_MODE_MAP_SCREEN,
    LZC_MODE_CUTSCENE,
    LZC_MODE_SA_X_CLOSE_UP,
    LZC_MODE_ERASE_SRAM_MENU,
    LZC_MODE_FILE_SELECT_OR_INTRO,
    LZC_MODE_GAME_OVER,
    LZC_MODE_ENDING,
    LZC_MODE_SR388_COLLISION_DEATH,
    LZC_MODE_CREDITS,
    LZC_MODE_DEMO,
    LZC_MODE_UNKNOWN,
    LZC_MODE_DEBUG,
    LZC_MODE_COUNT
} lzc_game_mode_t;

/* Returns false for an out-of-range mode or NULL output pointer. */
bool lzc_lookup_observed_mode_target(int16_t mode, uint32_t *rom_address_out);

#endif
