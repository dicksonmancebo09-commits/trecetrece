// Targeted, read-only-in-source Metroid Fusion AMTE bootstrap audit.
// Ghidra will save disassembly annotations in the analysis project only.
// The original ROM file is never written by this script.

import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.ArmDisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;

public class MetroidFusionBootstrapAudit extends GhidraScript {

    private static final long ROM_BASE = 0x08000000L;

    private String hex(long value) {
        return String.format("0x%08X", value);
    }

    private long readWord(long virtualAddress) throws Exception {
        byte[] bytes = new byte[4];
        currentProgram.getMemory().getBytes(toAddr(virtualAddress), bytes);
        return ((long) bytes[0] & 0xffL)
            | (((long) bytes[1] & 0xffL) << 8)
            | (((long) bytes[2] & 0xffL) << 16)
            | (((long) bytes[3] & 0xffL) << 24);
    }

    private void printWord(String label, long virtualAddress) throws Exception {
        long value = readWord(virtualAddress);
        println(label + " | address=" + hex(virtualAddress)
            + " | file_offset=" + hex(virtualAddress - ROM_BASE)
            + " | value=" + hex(value));
    }

    private void decodeWindow(
            String label,
            long start,
            long end,
            boolean thumbMode) throws Exception {

        Address first = toAddr(start);
        Address last = toAddr(end);
        AddressSet restricted = new AddressSet(first, last);

        println("");
        println("===== " + label + " =====");
        println("MODE=" + (thumbMode ? "THUMB" : "ARM"));
        println("RANGE=" + hex(start) + " .. " + hex(end));

        ArmDisassembleCommand command =
            new ArmDisassembleCommand(first, restricted, thumbMode);
        command.enableCodeAnalysis(false);
        boolean success = command.applyTo(currentProgram, monitor);

        println("DISASSEMBLE_START=" + first + " | success=" + success);
        println("REACHABLE_INSTRUCTIONS_WITHIN_WINDOW=");

        // Print only instruction units Ghidra actually decoded by following
        // control flow from this seed. Do not force-disassemble every halfword
        // after an unconditional branch: those bytes may be data or another
        // independently entered code region.
        ghidra.program.model.listing.InstructionIterator iterator =
            currentProgram.getListing().getInstructions(restricted, true);

        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();

            byte[] bytes = new byte[instruction.getLength()];
            currentProgram.getMemory().getBytes(
                instruction.getAddress(), bytes);

            StringBuilder raw = new StringBuilder();
            for (byte value : bytes) {
                raw.append(String.format("%02X ", value & 0xff));
            }

            long fileOffset =
                instruction.getAddress().getOffset() - ROM_BASE;

            println(instruction.getAddress()
                + " | file_offset=" + String.format("0x%06X", fileOffset)
                + " | " + raw.toString().trim()
                + " | " + instruction);

            Address[] flows = instruction.getFlows();
            if (flows != null) {
                for (Address flow : flows) {
                    println("    FLOW -> " + flow);
                }
            }
        }
    }

    @Override
    protected void run() throws Exception {
        println("METROID FUSION AMTE - BOOTSTRAP AUDIT");
        println("GHIDRA_LANGUAGE="
            + currentProgram.getLanguageID().getIdAsString());
        println("IMAGE_BASE=" + currentProgram.getImageBase());

        if (!"ARM:LE:32:v4t".equals(
                currentProgram.getLanguageID().getIdAsString())) {
            throw new IllegalStateException(
                "Expected ARM:LE:32:v4t; refusing to disassemble with another language.");
        }

        Address base = toAddr(ROM_BASE);
        MemoryBlock romBlock = currentProgram.getMemory().getBlock(base);
        if (romBlock == null || !romBlock.isInitialized()) {
            throw new IllegalStateException(
                "Expected initialized ROM memory block at " + hex(ROM_BASE));
        }

        println("ROM_BLOCK=" + romBlock.getName());
        println("ROM_BLOCK_START=" + romBlock.getStart());
        println("ROM_BLOCK_END=" + romBlock.getEnd());

        println("");
        println("===== LITERAL DATA =====");
        printWord("SYSTEM_STACK_LITERAL", ROM_BASE + 0xF4);
        printWord("IRQ_STACK_LITERAL", ROM_BASE + 0xF8);
        printWord("IRQ_VECTOR_LITERAL", ROM_BASE + 0xFC);
        printWord("THUMB_ENTRY_POINTER_LITERAL", ROM_BASE + 0x100);
        printWord("FLAG_POINTER_LITERAL_0790", ROM_BASE + 0x790);
        printWord("FLAG_POINTER_LITERAL_0794", ROM_BASE + 0x794);
        printWord("DISPLAY_INIT_POINTER_0834", ROM_BASE + 0x834);
        printWord("DISPLAY_INIT_POINTER_0838", ROM_BASE + 0x838);

        decodeWindow(
            "GBA ENTRY BRANCH",
            ROM_BASE,
            ROM_BASE + 3,
            false
        );

        decodeWindow(
            "ARM BOOTSTRAP AND INTERWORKING",
            ROM_BASE + 0xC0,
            ROM_BASE + 0xF3,
            false
        );

        decodeWindow(
            "ARM IRQ HANDLER PROLOGUE",
            ROM_BASE + 0x104,
            ROM_BASE + 0x127,
            false
        );

        decodeWindow(
            "THUMB ENTRY BLOCK",
            ROM_BASE + 0x230,
            ROM_BASE + 0x237,
            true
        );

        decodeWindow(
            "THUMB ENTRY CONTINUATION",
            ROM_BASE + 0x238,
            ROM_BASE + 0x257,
            true
        );

        decodeWindow(
            "THUMB UNCONDITIONAL BRANCH DESTINATION",
            ROM_BASE + 0x766,
            ROM_BASE + 0x785,
            true
        );

        decodeWindow(
            "THUMB BL DESTINATION",
            ROM_BASE + 0x798,
            ROM_BASE + 0x7B7,
            true
        );

        decodeWindow(
            "THUMB DISPLAY INITIALIZATION CONTINUATION",
            ROM_BASE + 0x7B8,
            ROM_BASE + 0x7D7,
            true
        );

        decodeWindow(
            "THUMB CALL TARGET 0x080047A8",
            ROM_BASE + 0x47A8,
            ROM_BASE + 0x47C7,
            true
        );

        println("");
        println("===== AUDIT LIMITS =====");
        println("Only the listed ARM/Thumb windows were disassembled.");
        println("No full-ROM auto-analysis was run by this script.");
        println("No bytes in the original ROM were modified.");
        println("Interpret handler and destination semantics only after reviewing the printed instructions and flow targets.");
        println("===== AUDIT COMPLETE =====");
    }
}
