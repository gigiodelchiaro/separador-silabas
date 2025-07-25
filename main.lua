-- Define sets
local CHAR_SETS = {
    VOGAIS_FRACAS = "iouïöüy",
    VOGAIS_FORTES = "aeáéóàèòãẽõâêôäëöíúìùĩũîû",
    CONSOANTES_FORTES = "bcdfgjkpqtvwxyzç",
    CONSOANTES_LIQUIDAS = "lr",
    CONSOANTES_NASAIS = "mn",
    CONSOANTES_SIBILANTES = "s",
    
    DIGRAFOS = {"ch", "lh", "nh", "gu", "qu"},
    
    -- Combined sets (computed below)
    LETRAS = nil,
    CONSOANTES = nil,
    VOGAIS = nil,
}

-- Compute combined sets
CHAR_SETS.VOGAIS = CHAR_SETS.VOGAIS_FRACAS .. CHAR_SETS.VOGAIS_FORTES
CHAR_SETS.CONSOANTES = CHAR_SETS.CONSOANTES_FORTES .. 
                      CHAR_SETS.CONSOANTES_LIQUIDAS .. 
                      CHAR_SETS.CONSOANTES_NASAIS .. 
                      CHAR_SETS.CONSOANTES_SIBILANTES
CHAR_SETS.LETRAS = CHAR_SETS.VOGAIS .. CHAR_SETS.CONSOANTES

-- Special operators/constants
local EQUAL = {}  -- Special marker for equal characters
local ANY = {}    -- Special marker for any character
local NOT_SET = {} -- Special marker for characters not in a set

-- Internal separator for marking syllable boundaries
local INTERNAL_SEPARATOR = "@"

-- Helper function to check if character is in a set
local function char_in_set(char, set_string)
    return string.find(set_string, char) ~= nil
end

-- Helper function to check if a substring is a digraph
local function is_digraph(text, pos)
    for _, digraph in ipairs(CHAR_SETS.DIGRAFOS) do
        if string.sub(text, pos, pos + #digraph - 1) == digraph then
            return true, digraph
        end
    end
    return false, nil
end

-- Convert text to character array handling digraphs
local function text_to_chars(text)
    local chars = {}
    local i = 1
    while i <= #text do
        local is_dig, digraph = is_digraph(text, i)
        if is_dig then
            table.insert(chars, digraph)
            i = i + #digraph
        else
            table.insert(chars, string.sub(text, i, i))
            i = i + 1
        end
    end
    return chars
end

-- Convert character array back to string
local function chars_to_string(chars)
    return table.concat(chars)
end

-- Advanced pattern matching system
local function match_pattern(chars, pos, pattern)
    if pos >= #chars then return false end
    
    local current_char = chars[pos] or ""
    local next_char = chars[pos + 1] or ""
    
    -- Handle EQUAL operator
    if pattern[1] == EQUAL then
        return current_char == next_char
    end
    
    -- Handle standard set matching
    local match1 = true
    local match2 = true
    
    if pattern[1] == ANY then
        match1 = true
    elseif type(pattern[1]) == "string" then
        match1 = char_in_set(current_char, pattern[1])
    end
    
    if pattern[2] == EQUAL then
        match2 = current_char == next_char
    elseif pattern[2] == ANY then
        match2 = true
    elseif type(pattern[2]) == "string" then
        match2 = char_in_set(next_char, pattern[2])
    end
    
    return match1 and match2
end

-- Rule structure
local function create_rule(pattern, position, description)
    return {
        pattern = pattern,
        position = position,
        description = description or "Unnamed rule"
    }
end

-- Syllabification rules
local SYLLABIFICATION_RULES = {
    create_rule({ANY, EQUAL}, 1, "Repeated character"),
}

-- Main syllabification function
local function syllabify_word(word)
    -- Handle hyphens first
    if string.find(word, "%-") then
        local parts = {}
        for part in string.gmatch(word, "[^-]+") do
            table.insert(parts, syllabify_word(part))
        end
        return table.concat(parts, "-")
    end
    
    local chars = text_to_chars(word:lower())
    if #chars <= 1 then
        return word
    end
    
    -- Apply rules from left to right
    local separators = {} -- positions where separators should be inserted
    
    for i = 1, #chars - 1 do
        for _, rule in ipairs(SYLLABIFICATION_RULES) do
            if match_pattern(chars, i, rule.pattern) then
                local insert_pos = i + rule.position - 1
                if insert_pos >= 1 and insert_pos <= #chars then
                    separators[insert_pos] = true
                    break -- Apply first matching rule at each position
                end
            end
        end
    end
    
    -- Insert separators
    local result_chars = {}
    for i = 1, #chars do
        table.insert(result_chars, chars[i])
        if separators[i] and i < #chars then
            table.insert(result_chars, INTERNAL_SEPARATOR)
        end
    end
    
    return chars_to_string(result_chars)
end

-- Function to clean up special cases (like gu/qu exceptions)
local function post_process_syllabification(syllabified_word)
    local result = syllabified_word
    
    -- Handle gu/qu exceptions (keep them together in certain contexts)
    result = string.gsub(result, "g@u", "gu")
    result = string.gsub(result, "q@u", "qu")
    
    -- Handle common vowel combinations that should stay together
    -- This is a simplified approach - you might want more sophisticated rules
    
    return result
end

-- Main function
local function syllabify(word)
    local syllabified = syllabify_word(word)
    return post_process_syllabification(syllabified)
end

-- Test words
local TEST_WORDS = {
    "saia",       -- Hiato
    "faixa",      -- Hiato
    "ritmo",      -- ConsonantNasal
    "sublinhar",  -- ConsLiquidVowel
    "agua",       -- Exception_GU_QU_Cleanup
    "linguica",   -- Exception_GU_QU_Cleanup, Exception_U_Vowel interaction
    "rua",        -- Exception_U_Vowel
    "maçã",       -- Test accented characters
    "pão",        -- Test accented characters
    "aeroporto",  -- Hiato example
    "casa",       -- VCV
    "passo",      -- Repeated letters
    "galinha",    -- Digraph
    "abacaxi",    -- VCV
    "rato",       -- Simple VCV
    "submarino",  -- More complex
    "coelho",     -- Digraph
    "carro",      -- Repeated letters
    "descer",     -- ConsonantSibilant
    "psicologia", -- ConsonantSibilant
    "pneumonia",  -- Complex start (will be rough without specific 'pn' rules)
    "transporte", -- Multiple internal splits
    "todo-poderoso" -- hyphen rule
}

-- Test loop
print("=== Portuguese Syllabification Test ===")
print("")

for i, word in ipairs(TEST_WORDS) do
    local result = syllabify(word)
    local display_result = string.gsub(result, INTERNAL_SEPARATOR, "-") -- Use | for display
    print(string.format("%2d. %-15s -> %s", i, word, display_result))
end

print("")
print("=== Rule Summary ===")
print("Total rules: " .. #SYLLABIFICATION_RULES)
for i, rule in ipairs(SYLLABIFICATION_RULES) do
    print(string.format("%2d. %s", i, rule.description))
end

-- -- Additional helper function to count syllables
-- local function count_syllables(word)
--     local syllabified = syllabify(word)
--     local count = 1 -- At least one syllable
--     count = count + select(2, string.gsub(syllabified, INTERNAL_SEPARATOR, ""))
--     return count
-- end

-- print("")
-- print("=== Syllable Counts ===")
-- for _, word in ipairs(TEST_WORDS) do
--     local count = count_syllables(word)
--     print(string.format("%-15s: %d syllable%s", word, count, count ~= 1 and "s" or ""))
-- end