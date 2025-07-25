local json = require("cjson")
local socket = require("socket")
local lanes = require("lanes").configure()

-- Configuration
local DICT_FILE = "dictionary/dictionary.json"
local REPORT_FILE = "report.txt"
local THREAD_COUNT = 4


local function load_dictionary()
    -- Load dictionary
    local file = io.open(DICT_FILE, "r")
    if not file then error("Could not open dictionary file") end
    local content = file:read("*all")
    file:close()
    return json.decode(content)
end

-- Execute main.lua with a word and get output
local function execute_main(word)
    local command = string.format('lua main.lua --word %s', word)
    local handle = io.popen(command)
    local result = handle:read("*a")
    handle:close()
    return result:match("^%s*(.-)%s*$")  -- trim whitespace
end

-- Format syllables as expected output
local function format_syllables(syllables)
    return table.concat(syllables, "-")
end

-- Worker thread function
local worker_thread = lanes.gen("*", function(words_chunk)
    local results = {}
    for _, entry in ipairs(words_chunk) do
        local expected = format_syllables(entry.syllables)
        local success, output = pcall(execute_main, entry.word)
        if not success or not output then
            output = "ERROR"
        end
        table.insert(results, {
            word = entry.word,
            expected = expected,
            obtained = output,
            correct = (output == expected)
        })
    end
    return results
end)

-- Split table into chunks for threading
local function split_table(t, n)
    local chunks = {}
    for i = 1, n do chunks[i] = {} end
    for i, v in ipairs(t) do
        table.insert(chunks[(i - 1) % n + 1], v)
    end
    return chunks
end

-- Create progress bar
local function create_progress_bar(current, total, width)
    width = width or 50
    local progress = current / total
    local bar_width = math.floor(width * progress)
    local bar = string.rep("█", bar_width) .. string.rep("░", width - bar_width)
    return string.format("[%s] %d/%d (%.1f%%)", bar, current, total, progress * 100)
end

-- Estimate remaining time
local function format_time(seconds)
    if seconds < 60 then
        return string.format("%ds", seconds)
    elseif seconds < 3600 then
        return string.format("%dm%ds", math.floor(seconds/60), seconds%60)
    else
        return string.format("%dh%dm", math.floor(seconds/3600), math.floor((seconds%3600)/60))
    end
end

-- Main execution
local function main()
    -- Load dictionary
    local dictionary = load_dictionary()
    local total_words = #dictionary
    print(string.format("Loaded %d words from dictionary", total_words))

    -- Split work among threads
    local chunks = split_table(dictionary, THREAD_COUNT)
    local futures = {}
    local processed_results = {}

    -- Start threads
    for i, chunk in ipairs(chunks) do
        local future = worker_thread(chunk)
        table.insert(futures, future)
        processed_results[i] = false
    end

    -- Collect results with progress tracking
    local all_results = {}
    local completed_threads = 0
    local last_update = 0
    local start_time = socket.gettime()

    while completed_threads < #futures do
        for i, future in ipairs(futures) do
            if future.status == "done" and not processed_results[i] then
                local results = future[1]  -- Get the return value
                for _, result in ipairs(results) do
                    table.insert(all_results, result)
                end
                processed_results[i] = true
                completed_threads = completed_threads + 1
            end
        end

        -- Update progress
        local current = #all_results
        if current > last_update then
            local elapsed = socket.gettime() - start_time
            local rate = current / elapsed
            local remaining = (total_words - current) / rate
            local progress_bar = create_progress_bar(current, total_words)
            local time_info = string.format("ETA: %s", format_time(remaining))
            io.write(string.format("\r%s %s", progress_bar, time_info))
            io.flush()
            last_update = current
        end

        socket.sleep(0.1)
    end

    -- Final progress update
    local elapsed_time = socket.gettime() - start_time
    print(string.format("\nCompleted in %.2fs", elapsed_time))

    -- Generate report
    local correct_count = 0
    local wrong_entries = {}

    for _, result in ipairs(all_results) do
        if result.correct then
            correct_count = correct_count + 1
        else
            table.insert(wrong_entries, result)
        end
    end

    local accuracy = (correct_count / total_words) * 100

    -- Write report
    local report = io.open(REPORT_FILE, "w")
    report:write(string.format("Accuracy: %.2f%% (%d/%d correct)\n\n", accuracy, correct_count, total_words))

    if #wrong_entries > 0 then
        report:write("Incorrect entries:\n")
        report:write("==================\n")
        for _, entry in ipairs(wrong_entries) do
            report:write(string.format("Word: %s\n", entry.word))
            report:write(string.format("Expected: %s\n", entry.expected))
            report:write(string.format("Obtained: %s\n", entry.obtained))
            report:write("\n")
        end
    else
        report:write("All words processed correctly!\n")
    end
    report:close()

    print(string.format("Report written to %s", REPORT_FILE))
    print(string.format("Accuracy: %.2f%%", accuracy))
end

main()