#include <assert.h>
#include <stdint.h>
#include "game_mode_dispatch.h"

int main(void)
{
    uint32_t address = 0;

    assert(lzc_lookup_observed_mode_target(LZC_MODE_TITLE, &address));
    assert(address == UINT32_C(0x080002B4));

    assert(lzc_lookup_observed_mode_target(LZC_MODE_IN_GAME, &address));
    assert(address == UINT32_C(0x08000448));

    assert(lzc_lookup_observed_mode_target(LZC_MODE_DEBUG, &address));
    assert(address == UINT32_C(0x0800074C));

    assert(!lzc_lookup_observed_mode_target(-1, &address));
    assert(!lzc_lookup_observed_mode_target(LZC_MODE_COUNT, &address));
    assert(!lzc_lookup_observed_mode_target(LZC_MODE_TITLE, NULL));

    return 0;
}
