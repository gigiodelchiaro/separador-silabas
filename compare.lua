local json = require("json")
local main = require("main")

local file = io.open("dictionary.json", "r")
if not file then
  print("Error: Could not open dictionary.json")
  return
end

local content = file:read("*a")
file:close()

local data = json.decode(content)

local total_words = 0
local correct_words = 0

for _, entry in ipairs(data) do
  total_words = total_words + 1
  local word = entry.word
  local expected_syllables = entry.syllables

  local actual_syllables = main.separate_syllables(word)

  local is_correct = true
  if #actual_syllables ~= #expected_syllables then
    is_correct = false
  else
    for i = 1, #actual_syllables do
      if actual_syllables[i] ~= expected_syllables[i] then
        is_correct = false
        break
      end
    end
  end

  if is_correct then
    correct_words = correct_words + 1
  else
    print("Mismatch for word: " .. word)
    print("  Expected: " .. table.concat(expected_syllables, "-"))
    print("  Actual:   " .. table.concat(actual_syllables, "-"))
  end
end

print("\nComparison complete.")
print("Total words: " .. total_words)
print("Correctly separated: " .. correct_words)
print("Accuracy: " .. (correct_words / total_words * 100) .. "%")
