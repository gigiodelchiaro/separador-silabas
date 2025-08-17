// compare.ts
import fs from 'fs';
import path from 'path';
import tonic from '../tonic'; // Import the tonic function from tonic.ts

// Define an interface for the dictionary entry structure
interface DictionaryEntry {
    word: string;
    description: string;
    syllables: string[];
    tonic: number;
}

/**
 * Runs a comparison between the expected tonic syllables in a dictionary
 * and the predictions from the 'tonic' function. Generates a report.
 *
 * @param jsonFilePath The path to the JSON dictionary file.
 * @param outputFilePath The path to the output text file where the report will be saved.
 */
function runComparison(jsonFilePath: string, outputFilePath: string): void {
    let correctCount = 0;
    let incorrectWords: { word: string; expected: number; received: number | string; syllables: string[] }[] = [];
    let totalWords = 0;
    let reportContent: string[] = []; // Array to store lines of the report

    // Helper function to add lines to the report content and optionally print to console
    const logReport = (message: string, toConsole: boolean = true) => {
        reportContent.push(message);
        if (toConsole) {
            console.log(message); // Keep console output for immediate feedback
        }
    };

    const errorReport = (message: string, toConsole: boolean = true) => {
        reportContent.push(`ERROR: ${message}`);
        if (toConsole) {
            console.error(`ERROR: ${message}`); // Keep console error for immediate feedback
        }
    };


    try {
        // Resolve the file path to ensure it works correctly regardless of where the script is run
        const absoluteJsonPath = path.resolve(jsonFilePath);

        // Read the JSON file content
        const fileContent = fs.readFileSync(absoluteJsonPath, 'utf-8');

        // Parse the JSON content into an array of DictionaryEntry objects
        const dictionary: DictionaryEntry[] = JSON.parse(fileContent);

        totalWords = dictionary.length;

        if (totalWords === 0) {
            logReport("The dictionary file is empty or contains no entries.");
            fs.writeFileSync(outputFilePath, reportContent.join('\n')); // Write to file even if empty
            return;
        }

        // Iterate through each entry in the dictionary
        for (const entry of dictionary) {
            const { word, syllables, tonic: expectedTonic } = entry;

            let predictedTonic: number | string;
            try {
                // Call the tonic function with the syllables array
                predictedTonic = tonic(syllables);
            } catch (error: any) {
                // Handle errors from the tonic function (e.g., if syllables array is empty)
                errorReport(`Warning: Error processing word "${word}": ${error.message}`, false); // Don't print warnings to console during loop
                predictedTonic = `Error: ${error.message}`;
            }

            // Compare the predicted tonic with the expected tonic from the dictionary
            if (predictedTonic === expectedTonic) {
                correctCount++;
            } else {
                incorrectWords.push({
                    word: word,
                    expected: expectedTonic,
                    received: predictedTonic,
                    syllables: syllables
                });
            }
        }

        // Generate the report content
        logReport("\n--- Tonic Prediction Report ---", false); // Only add to reportContent, not console for final report
        logReport(`Total words processed: ${totalWords}`, false);
        logReport(`Correct predictions: ${correctCount}`, false);
        logReport(`Incorrect predictions: ${incorrectWords.length}`, false);

        const accuracy = totalWords > 0 ? (correctCount / totalWords) * 100 : 0;
        logReport(`Overall Accuracy: ${accuracy.toFixed(2)}%`, false);

        if (incorrectWords.length > 0) {
            logReport("\n--- Incorrect Words ---", false);
            incorrectWords.forEach(item => {
                logReport(`Word: "${item.word}"`, false);
                logReport(`  Syllables: [${item.syllables.map(s => `"${s}"`).join(', ')}]`, false);
                logReport(`  Expected Tonic (from dictionary): ${item.expected}`, false);
                logReport(`  Predicted Tonic (by tonic.ts): ${item.received}`, false);
                logReport("---", false);
            });
        } else {
            logReport("\nAll words predicted correctly! 🎉", false);
        }

        // Write the accumulated report content to the specified output file
        fs.writeFileSync(outputFilePath, reportContent.join('\n'), 'utf-8');
        console.log(`\nReport successfully written to: ${outputFilePath}`); // Confirm output to user

    } catch (error: any) {
        let errorMessage: string;
        if (error.code === 'ENOENT') {
            errorMessage = `File not found at '${jsonFilePath}'. Please ensure 'dict.json' exists or provide the correct path.`;
        } else if (error instanceof SyntaxError) {
            errorMessage = `Invalid JSON format in '${jsonFilePath}'. Please check the file for syntax errors. Message: ${error.message}`;
        } else {
            errorMessage = `An unexpected error occurred: ${error.message}`;
        }
        errorReport(`\nAn error occurred while reading or processing the dictionary file:`);
        errorReport(errorMessage);
        // Attempt to write the error message to the report file if possible
        try {
            fs.writeFileSync(outputFilePath, reportContent.join('\n'), 'utf-8');
            console.error(`Error details also written to: ${outputFilePath}`);
        } catch (fileWriteError: any) {
            console.error(`Failed to write error report to file: ${fileWriteError.message}`);
        }
    }
}

// Get the JSON file path and output file path from command line arguments
// Usage: node compare.js [path/to/your/dict.json] [path/to/output_report.txt]
const dictionaryPath = process.argv[2] || './dict.json';
const outputReportPath = process.argv[3] || './tonic_report.txt'; // Default output file name

runComparison(dictionaryPath, outputReportPath);