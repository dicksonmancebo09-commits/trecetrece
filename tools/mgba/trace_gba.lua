-- LATINO AMÉRICA Zector Cero — mGBA Lua trace helper
--
-- Load in mGBA GUI: Tools -> Scripting -> Load Script.
-- Create private-roms/diagnostics/ before loading.
-- This script records execution state; it does not patch the ROM.
-- AUTO_INPUT defaults to false so loading the trace cannot unexpectedly press buttons.
-- For a controlled test, set AUTO_INPUT = true and use a new/isolated save.

local OUT_DIR = "private-roms/diagnostics"
local AUTO_INPUT = false
local SAMPLE_INTERVAL_FRAMES = 30
local STOP_AFTER_FRAME = 1800

local CAPTURE_FRAMES = { 1, 420, 600, 780, 1500, 1680 }
local AUTO_INPUT_STEPS = {
    { start_frame = 422, end_frame_exclusive = 428, key = C.GBA_KEY.START },
    { start_frame = 610, end_frame_exclusive = 616, key = C.GBA_KEY.A },
    { start_frame = 1560, end_frame_exclusive = 1602, key = C.GBA_KEY.RIGHT },
}

local run_tag = os.date("%Y%m%d-%H%M%S")
local log_path = OUT_DIR .. "/mgba-trace-" .. run_tag .. ".csv"
local trace_file, open_error = io.open(log_path, "w")
if not trace_file then
    console:log("GBA trace error: cannot open " .. log_path .. ": " .. tostring(open_error))
    return
end

local start_frame = emu:currentFrame()
local last_logged_frame = -1
local closed = false

local function hex(value)
    if type(value) == "number" then
        return string.format("0x%X", value)
    end
    return tostring(value)
end

local function read8(address)
    local ok, value = pcall(function() return emu:read8(address) end)
    if ok then return hex(value) end
    return "ERR"
end

local function read16(address)
    local ok, value = pcall(function() return emu:read16(address) end)
    if ok then return hex(value) end
    return "ERR"
end

local function read_register(name)
    local ok, value = pcall(function() return emu:readRegister(name) end)
    if ok then return tostring(value) end
    return "ERR"
end

local function write_record(relative_frame, event_name)
    if closed then return end
    trace_file:write(table.concat({
        tostring(relative_frame),
        event_name or "sample",
        read_register("pc"),
        read_register("lr"),
        read_register("sp"),
        read_register("cpsr"),
        read8(0x03000BDE),  -- gMainGameMode from the known AMTE decomp layout
        read16(0x03000BE0), -- gSubGameMode1
        read16(0x03000BE2), -- gSubGameMode2
        read16(0x04000000), -- DISPCNT
        read16(0x0400000A), -- BG1CNT
        read16(0x0400000C), -- BG2CNT
        read16(0x0400000E), -- BG3CNT
        read16(0x04000006), -- VCOUNT
        read16(0x04000130)  -- KEYINPUT
    }, ",") .. "\n")
    trace_file:flush()
    last_logged_frame = relative_frame
end

local function take_capture(relative_frame)
    local filename = string.format("%s/mgba-%s-frame-%04d.png", OUT_DIR, run_tag, relative_frame)
    local ok, err = pcall(function() emu:screenshot(filename) end)
    if ok then
        write_record(relative_frame, "screenshot:" .. filename)
        console:log("GBA trace screenshot: " .. filename)
    else
        write_record(relative_frame, "screenshot-error:" .. tostring(err))
        console:log("GBA trace screenshot failed: " .. tostring(err))
    end
end

local function apply_automated_keys(relative_frame)
    if not AUTO_INPUT then return end
    local keys = {}
    for _, step in ipairs(AUTO_INPUT_STEPS) do
        if relative_frame >= step.start_frame and relative_frame < step.end_frame_exclusive then
            keys[#keys + 1] = step.key
        end
    end
    -- The API accepts a bitmask made from key-index values. This intentionally
    -- releases all keys between scripted presses to avoid sticky input.
    emu:setKeys(util.makeBitmask(keys))
end

trace_file:write("relative_frame,event,pc,lr,sp,cpsr,main_game_mode,sub_game_mode_1,sub_game_mode_2,DISPCNT,BG1CNT,BG2CNT,BG3CNT,VCOUNT,KEYINPUT\n")
trace_file:write("# game_title=" .. tostring(emu:getGameTitle()) .. ",game_code=" .. tostring(emu:getGameCode()) .. "\n")
trace_file:flush()
console:log("GBA trace started: " .. log_path)
console:log("ROM: " .. tostring(emu:getGameTitle()) .. " / " .. tostring(emu:getGameCode()))
if not AUTO_INPUT then
    console:log("AUTO_INPUT=false: no buttons will be pressed by this script.")
end

local callback_id
callback_id = callbacks:add("frame", function()
    if closed then return end
    local relative_frame = emu:currentFrame() - start_frame
    apply_automated_keys(relative_frame)

    local should_capture = false
    for _, target in ipairs(CAPTURE_FRAMES) do
        if relative_frame == target then
            should_capture = true
            break
        end
    end

    if relative_frame % SAMPLE_INTERVAL_FRAMES == 0 and relative_frame ~= last_logged_frame then
        write_record(relative_frame, "sample")
    end
    if should_capture then
        take_capture(relative_frame)
    end
    if relative_frame >= STOP_AFTER_FRAME then
        write_record(relative_frame, "trace-complete")
        callbacks:remove(callback_id)
        closed = true
        trace_file:flush()
        trace_file:close()
        console:log("GBA trace complete. Inspect CSV and screenshots in " .. OUT_DIR)
    end
end)

callbacks:add("crashed", function()
    if not closed then
        write_record(emu:currentFrame() - start_frame, "EMULATOR_CRASH_CALLBACK")
        take_capture(emu:currentFrame() - start_frame)
        trace_file:flush()
        trace_file:close()
        closed = true
    end
end)
