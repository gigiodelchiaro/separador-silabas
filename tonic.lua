local strong_accents = "áéíóúàèìòùâêîôû"
local weak_accents = "ãẽĩõũ"

local accent_categories = {
    "áéíóú",   -- Acute (strong)
    "àèìòù",   -- Grave (strong)
    "âêîôû",   -- Circumflex (strong)
    "ãẽĩõũ"    -- Tilde (weak)
}

-- CORRECTED: This version iterates over UTF-8 characters correctly.
local function has_char(str, chars)
    -- The pattern '([%z\1-\127\194-\244][\128-\191]*)' correctly matches multi-byte UTF-8 characters.
    for char_in_str in str:gmatch('([%z\1-\127\194-\244][\128-\191]*)') do
        if chars:find(char_in_str, 1, true) then
            return true
        end
    end
    return false
end

local function split_word(word, separator)
    local syllables = {}
    -- The pattern is now built dynamically to exclude the provided separator.
    for syllable in word:gmatch("[^" .. separator .. "]+") do
        table.insert(syllables, syllable:lower())
    end
    return syllables
end

local function tonic(word_separated)
    if #word_separated == 1 then
        return 1
    end

    -- Check for accents in hierarchical order
    for _, accent_group in ipairs(accent_categories) do
        for i = #word_separated, 1, -1 do
            local syllable = word_separated[i]
            if has_char(syllable, accent_group) then
                return #word_separated - i + 1
            end
        end
    end

    -- If no accented syllable, apply default rules
    local last_syllable = word_separated[#word_separated]
    local hyphen_count = 0
    for char in last_syllable:gmatch("-") do
        hyphen_count = hyphen_count + 1
    end

    local last_syllable_before_hyphen = ""
    if hyphen_count > 0 and #word_separated >= 1 + hyphen_count then
        last_syllable_before_hyphen = word_separated[#word_separated - hyphen_count]
    end

    local ending_patterns = {
        "is?%W*$",      -- matches "i" or "is"
        "[uzrlxn]%W*$", -- matches single letters: u,z,r,l,x,n
        "im%W*$",
        "us%W*$",
        "ums?%W*$",
        "ps%W*$",
        "om%W*$",
        "ons?%W*$"
    }

    local function check_patterns(syllable)
        for _, pattern in ipairs(ending_patterns) do
            if syllable:find(pattern) then
                return true
            end
        end
        return false
    end

    if check_patterns(last_syllable) then
        return 1
    elseif hyphen_count > 0 and check_patterns(last_syllable_before_hyphen) then
        return hyphen_count + 1
    end

    return 2
end

      
local function main()
    local word = nil
    local full = false
    local separator = "-" -- Default separator
    
    for i = 1, #arg do
        if arg[i] == "--word" and i + 1 <= #arg then
            word = arg[i + 1]
            i = i + 1
        elseif arg[i] == "--separator" and i + 1 <= #arg then
            separator = arg[i + 1]
            i = i + 1
        elseif arg[i] == "--full" then
            full = true
        end
    end
    
    if not word then
        print("Error: --word parameter is required")
        return 1
    end
    
    -- Pass the custom separator to the split_word function
    local syllables = split_word(word, separator)
    local tonic_number = tonic(syllables)
    
    if full then
        print("Word: " .. word)
        print("Syllables: " .. #syllables)
        print("Tonic syllable: " .. tonic_number)
    else
        print(tonic_number)
    end
    
    return 0
end

    

-- In some environments like online compilers, 'os.exit' might not be available
-- or 'arg' might be nil. Calling main() directly is safer for testing.
main()