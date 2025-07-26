-- Create a table to export functions
local M = {}

-- Define sets
local CHAR_SETS = {
    A = "a",
    E = "e",
    I = "i",
    O = "o",
    U = "u",
    VOGAIS_FRACAS = "iouïöüy",
    VOGAIS_FORTES = "aeáéóàèòãẽõâêôäëöíúìùĩũîû",
    CONSOANTES_FORTES = "bcdfgjkpqtvwxyzç",
    CONSOANTES_LIQUIDAS = "lr",
    CONSOANTES_NASAIS = "mn",
    S = "s",
    DIGRAFOS = {"ch", "lh", "nh", "gu", "qu"},
    -- Combined sets (computed below)
    LETRAS = nil,
    CONSOANTES = nil,
    VOGAIS = nil,
}
-- Compute combined sets
CHAR_SETS.VOGAIS = CHAR_SETS.VOGAIS_FRACAS .. CHAR_SETS.VOGAIS_FORTES .. CHAR_SETS.E
CHAR_SETS.CONSOANTES = CHAR_SETS.CONSOANTES_FORTES ..
                      CHAR_SETS.CONSOANTES_LIQUIDAS ..
                      CHAR_SETS.CONSOANTES_NASAIS ..
                      CHAR_SETS.S
CHAR_SETS.CONSOANTES_FRACAS = CHAR_SETS.CONSOANTES_LIQUIDAS ..
                    CHAR_SETS.CONSOANTES_NASAIS ..
                    CHAR_SETS.S
CHAR_SETS.LETRAS = CHAR_SETS.VOGAIS .. CHAR_SETS.CONSOANTES
-- Special operators/constants
local EQUAL = {}  -- Special marker for equal characters
local ANY = {}    -- Special marker for any character
-- Define NOT_SET as a function that creates a negation marker
local function NOT_SET(set_string)
    return { _not_set = true, set = set_string }
end

-- Internal separator for marking syllable boundaries
local INTERNAL_SEPARATOR = "@"
-- Helper function to check if character is in a set (MODIFIED)
local function char_in_set(char, set_spec)
    -- Check if set_spec is the NOT_SET marker table
    if type(set_spec) == "table" and set_spec._not_set then
        -- Return true if the character is NOT found in the specified set
        return string.find(set_spec.set, char) == nil
    -- Handle normal string sets and ANY/EQUAL (existing logic)
    elseif set_spec == ANY or set_spec == EQUAL then
         -- EQUAL is handled elsewhere, but kept for completeness if needed here
        return true
    elseif type(set_spec) == "string" then
        return string.find(set_spec, char) ~= nil
    end
    -- Default case (e.g., if set_spec is an unexpected type)
    return false
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
-- Convert text to character array handling digraphs and UTF-8 characters properly
local function text_to_chars(text)
    local chars = {}
    local i = 1
    while i <= #text do
        -- Check for digraphs first
        local is_dig, digraph = is_digraph(text, i)
        if is_dig then
            table.insert(chars, digraph)
            i = i + #digraph
        else
            -- Handle UTF-8 characters properly
            local byte = string.byte(text, i)
            local char_width = 1
            -- Determine UTF-8 character width
            if byte >= 0xF0 then
                char_width = 4  -- 4-byte UTF-8 character
            elseif byte >= 0xE0 then
                char_width = 3  -- 3-byte UTF-8 character
            elseif byte >= 0xC0 then
                char_width = 2  -- 2-byte UTF-8 character
            end
            table.insert(chars, string.sub(text, i, i + char_width - 1))
            i = i + char_width
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
-- Enhanced cleanup rule constructor
local function create_cleanup_rule(pattern, remove_index, description)
    return {
        pattern = pattern,           -- e.g., {CHAR_SETS.CONSOANTES_FORTES, "@", CHAR_SETS.CONSOANTES_LIQUIDAS .. CHAR_SETS.CONSOANTES_FRACAS}
        remove_index = remove_index, -- 1-based index of which "@" to remove (if multiple)
        description = description or "Unnamed cleanup rule"
    }
end
-- Syllabification rules
local SYLLABIFICATION_RULES = {
    create_rule({ANY, EQUAL}, 1, "Letras Iguais"),
    create_rule({CHAR_SETS.VOGAIS, CHAR_SETS.O}, 1, "Caso vogal-O"),
    create_rule({CHAR_SETS.VOGAIS_FRACAS, CHAR_SETS.VOGAIS_FORTES}, 1, "Hiato fraco"),
    create_rule({"ae", CHAR_SETS.VOGAIS_FORTES}, 1, "Hiato forte"),
    --create_rule({"ou", "i"}, 1, "Hiato o/u-i"),
    create_rule({CHAR_SETS.CONSOANTES_FORTES}, 0, "Consoantes Fortes"),
    create_rule({CHAR_SETS.CONSOANTES_FRACAS, CHAR_SETS.VOGAIS}, 0, "Consoantes Fracas"),
    create_rule({"bd", "s"}, 0, "Consoantes Fracas"),
}
-- Cleanup rules
local CLEANUP_RULES = {
    create_cleanup_rule({CHAR_SETS.CONSOANTES_FORTES, "@", CHAR_SETS.CONSOANTES_LIQUIDAS}, 2, "Remover separador entre consoantes fortes e liquidas"),
    create_cleanup_rule({"@", CHAR_SETS.CONSOANTES_FORTES, "@", CHAR_SETS.CONSOANTES_NASAIS .. "s"}, 1, "Remover separador entre consoantes fortes e fracas"),
    create_cleanup_rule({"@", CHAR_SETS.CONSOANTES_FORTES, "@", CHAR_SETS.CONSOANTES_FORTES}, 1, "Remover separador entre consoantes fortes"),
    create_cleanup_rule({"ã", "@", "o"}, 2, "Remover separador entre ã e o"),
}
-- Enhanced cleanup rule application
local function apply_cleanup_rules(syllabified)
    local chars = text_to_chars(syllabified)
    local separators_to_remove = {} -- Track which separator positions to remove
    -- First pass: identify separators to remove
    for i = 1, #chars do
        if chars[i] == INTERNAL_SEPARATOR then
            for _, rule in ipairs(CLEANUP_RULES) do
                local pattern = rule.pattern
                local pattern_len = #pattern
                local remove_idx = rule.remove_index
                -- Check if we have enough characters around this separator
                local start_pos = i - remove_idx + 1
                local end_pos = start_pos + pattern_len - 1
                if start_pos >= 1 and end_pos <= #chars then
                    local match = true
                    for j = 1, pattern_len do
                        local pattern_char = pattern[j]
                        local actual_char = chars[start_pos + j - 1]
                        if pattern_char == "@" then
                            if actual_char ~= INTERNAL_SEPARATOR then
                                match = false
                                break
                            end
                        elseif pattern_char == ANY then
                            -- Match anything
                        elseif type(pattern_char) == "string" then
                            if not char_in_set(actual_char, pattern_char) then
                                match = false
                                break
                            end
                        else
                            match = false
                            break
                        end
                    end
                    if match then
                        -- Mark the specific separator for removal
                        separators_to_remove[i] = true
                        break -- Apply first matching rule
                    end
                end
            end
        end
    end
    -- Second pass: build result without marked separators
    local new_chars = {}
    for i = 1, #chars do
        if chars[i] ~= INTERNAL_SEPARATOR or not separators_to_remove[i] then
            table.insert(new_chars, chars[i])
        end
    end
    return chars_to_string(new_chars)
end
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
    for _, digraph in ipairs(CHAR_SETS.DIGRAFOS) do
        result = string.gsub(result, digraph, "@" .. digraph)
    end
    -- create_rule({CHAR_SETS.VOGAIS, CHAR_SETS.I, CHAR_SETS.CONSOANTES_LIQUIDAS .. CHAR_SETS.CONSOANTES_NASAIS, NOT_SET(CHAR_SETS.VOGAIS)}, 1, "Caso vogal-ir"),
    result = string.gsub(result, "([aeou])(i[nmrlz])$", "%1@%2")

    --create_cleanup_rule({"@", "bs", "@"}, 1, "Caso bs"),
    result = string.gsub(result, "@bs@", "bs@")
    --create_cleanup_rule({"@", "d", "@", "q"}, 1, "Caso dq"),
    result = string.gsub(result, "@d@q", "d@q")
    --create_cleanup_rule({"aei", "oui", "mn"}, 1, "Caso cafarnaum e ainda"),
    result = string.gsub(result, "([aei])([oui])([mn])", "%1@%2%3")
    result = string.gsub(result, "([aeo])in", "%1@in")
    result = string.gsub(result, "([aeou])i@nh", "%1@i@nh")
    -- Apply cleanup rules
    -- result = string.gsub(result, "([".. CHAR_SETS.CONSOANTES .."])" .. "ui@([" ..CHAR_SETS.CONSOANTES_FORTES .. "])", "%1u@i@%2")
    --create_cleanup_rule({"gq", "u", "@", "ei"}, 1, "Caso queijo"),
    result = string.gsub(result, "([gq])u@([ei])", "%1u%2")
    result = apply_cleanup_rules(result)
    return result
end


-- Main syllabification function exposed
function M.syllabify(word)
    local syllabified = syllabify_word(word)
    return post_process_syllabification(syllabified)
end

-- Function to split syllabified word into a table of syllables
function M.split_syllables(syllabified_word_with_internal_separator)
    local parts = {}
    for part in string.gmatch(syllabified_word_with_internal_separator, "[^" .. INTERNAL_SEPARATOR .. "]+") do
        table.insert(parts, part)
    end
    return parts
end

-- Optionally, if you want to expose the raw separator for advanced usage
M.INTERNAL_SEPARATOR = INTERNAL_SEPARATOR

-- Return the module table
return M