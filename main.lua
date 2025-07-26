-- main.lua

local tonic_module = require("tonic")
local syllable_module = require("syllable")

local function print_usage()
    print([[
Usage: lua main.lua --word <word> [--tonic] [--syllable] [--full]

Options:
  --word WORD      The word to analyze (required)
  --tonic          Run tonic analysis
  --syllable       Run syllabification
  --full           Enable full output mode
]])
end

local function main(args)
    local word = nil
    local run_tonic = false
    local run_syllable = false
    local full = false

    local i = 1
    while i <= #args do
        local arg = args[i]
        if arg == "--word" then
            i = i + 1
            if i <= #args then
                word = args[i]
            else
                print("Error: --word requires a value.")
                print_usage()
                return 1
            end
        elseif arg == "--tonic" then
            run_tonic = true
        elseif arg == "--syllable" then
            run_syllable = true
        elseif arg == "--full" then
            full = true
        else
            print("Error: Unknown argument: " .. arg)
            print_usage()
            return 1
        end
        i = i + 1
    end

    if not word then
        print("Error: --word is required.")
        print_usage()
        return 1
    end

    -- If neither --tonic nor --syllable specified, default to both
    if not run_tonic and not run_syllable then
        run_tonic = true
        run_syllable = true
    end

    -- Run syllabification if needed (it's needed for tonic analysis as well)
    local syllables
    if run_syllable or run_tonic then
        -- Assuming syllable_module and its functions are defined elsewhere
        local syllabified_internal = syllable_module.syllabify(word)
        syllables = syllable_module.split_syllables(syllabified_internal)
    end

    if full then
        -- Consolidated and pretty output for full mode
        print("┌───────────────────────────────────┐")
        print("│         Análise de palavra        │")
        print("└───────────────────────────────────┘")
        print(string.format("Palavra: %s", word))
        print("───────────────────────────────────")

        if run_syllable then
            print(string.format("Sílabas: %s", table.concat(syllables, " - ")))
        end

        if run_tonic then
            -- Assuming tonic_module and its functions are defined elsewhere
            local tonic_number = tonic_module.tonic(syllables)
            local tonic_syllable_text = syllables[#syllables - tonic_number + 1]
            local tipo_silaba = nil
            if tonic_number == 1 then
                tipo_silaba = "oxítona"
            elseif tonic_number == 2 then
                tipo_silaba = "paroxítona"
            elseif tonic_number == 3 then
                tipo_silaba = "proparoxítona"
            else
                tipo_silaba = "???"
            end
            print(string.format("Sílaba tônica: '%s' (%s #%d)", tonic_syllable_text, tipo_silaba, tonic_number))
        end
        print("───────────────────────────────────")
        print("") -- Add a newline for better visual separation
    else
        -- Original non-full output behavior
        if run_syllable then
            print(table.concat(syllables, "-"))
        end

        if run_tonic then
            -- Assuming tonic_module and its functions are defined elsewhere
            local tonic_number = tonic_module.tonic(syllables)
            print(tonic_number)
        end
    end

    return 0
end

-- Start the program
os.exit(main(arg))