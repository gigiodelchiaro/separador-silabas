-- tonic.lua
local M = {} -- Create a module table

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
M.has_char = has_char -- Expose if needed, otherwise keep local

function M.split_word(word, separator)
    local syllables = {}
    -- The pattern is now built dynamically to exclude the provided separator.
    for syllable in word:gmatch("[^" .. separator .. "]+") do
        table.insert(syllables, syllable:lower())
    end
    return syllables
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

function M.tonic(word_separated)
    if #word_separated == 1 then
        return 1
    end

    -- Check for accents in hierarchical order
    for _, accent_group in ipairs(accent_categories) do
        for i = #word_separated, 1, -1 do
            local syllable = word_separated[i]
            if has_char(syllable, accent_group) then
                -- Return position from the end (1 for last, 2 for second to last, etc.)
                return #word_separated - i + 1
            end
        end
    end

    -- If no accented syllable, apply default rules
    local last_syllable = word_separated[#word_separated]
    local hyphen_count = 0
    -- This gmatch iterates over individual hyphens if they are part of a "syllable" as a result of split_word
    -- However, the logic for `hyphen_count` and `last_syllable_before_hyphen` seems to imply `word_separated`
    -- might contain parts of a hyphenated word. For a pure syllabification, `split_word` should ideally
    -- not yield hyphens as "syllables". Assuming `split_word` removes hyphens.
    -- If hyphens are *not* the separator, this loop will count them within the last "syllable" part.
    -- Clarification needed on how hyphens are handled in `word_separated` if `separator` is not "-".
    for char_idx = 1, #last_syllable do
        if string.sub(last_syllable, char_idx, char_idx) == "-" then
            hyphen_count = hyphen_count + 1
        end
    end

    local last_syllable_before_hyphen = ""
    -- This logic for `last_syllable_before_hyphen` is a bit complex if the separator is not a hyphen.
    -- It assumes `word_separated` segments are directly from a hyphenated word structure.
    -- Re-evaluating this part if `word_separated` comes from `M.split_word(word, some_separator)`
    -- and `some_separator` is NOT a hyphen, then `hyphen_count` will be 0 unless literal hyphens exist in syllables.
    -- Assuming `word_separated` here is a simple list of syllables, not including explicit hyphens as elements.
    if hyphen_count > 0 and #word_separated >= 1 + hyphen_count then
        last_syllable_before_hyphen = word_separated[#word_separated - hyphen_count]
    end

    if check_patterns(last_syllable) then
        return 1 -- Última sílaba (oxítona)
    elseif hyphen_count > 0 and check_patterns(last_syllable_before_hyphen) then
        -- This case needs careful consideration of what `hyphen_count` signifies
        -- in the context of `word_separated` from `split_word`.
        -- If `hyphen_count` here means the number of hyphens *within* the last syllable string,
        -- this logic might be misaligned with common syllabification where hyphens separate words/parts.
        -- For typical tonic syllable rules in Portuguese (e.g., paroxítona ending in 'l', 'r', 'z', 'x', 'n', 'ps', ditongos nasais),
        -- the focus is on the *ending* of the word/last syllable.
        -- Let's stick to the direct interpretation of the original code,
        -- but note this might need review based on actual hyphenation logic.
        return hyphen_count + 1
    end

    return 2 -- Penúltima sílaba (paroxítona) - default
end

-- Return the module table
return M