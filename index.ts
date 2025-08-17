
import tonic from './tonic';
import syllable from './syllable';

function printUsage(): void {
    console.log(`
Usage: bun run index.ts --word <word> [--tonic] [--syllable] [--full]

Options:
  --word WORD      The word to analyze (required)
  --tonic          Run tonic analysis
  --syllable       Run syllabification
  --full           Enable full output mode
`);
}

function main(args: string[]): number {
    let word: string | null = null;
    let runTonic: boolean = false;
    let runSyllable: boolean = false;
    let full: boolean = false;

    let i = 0;
    while (i < args.length) {
        const arg = args[i];
        if (arg === "--word") {
            i++;
            if (i < args.length) {
                word = args[i]!;
            } else {
                console.error("Error: --word requires a value.");
                printUsage();
                return 1;
            }
        } else if (arg === "--tonic") {
            runTonic = true;
        } else if (arg === "--syllable") {
            runSyllable = true;
        } else if (arg === "--full") {
            full = true;
        } else {
            console.error(`Error: Unknown argument: ${arg}`);
            printUsage();
            return 1;
        }
        i++;
    }

    if (!word) {
        console.error("Error: --word is required.");
        printUsage();
        return 1;
    }

    // If neither --tonic nor --syllable specified, default to both
    if (!runTonic && !runSyllable) {
        runTonic = true;
        runSyllable = true;
    }

    let syllables: string[] = [];
    if (runSyllable || runTonic) {
        syllables = syllable(word).split("@");
    }

    if (full) {
        // Consolidated and pretty output for full mode
        console.log("┌───────────────────────────────────┐");
        console.log("│         Análise de palavra        │");
        console.log("└───────────────────────────────────┘");
        console.log(`Palavra: ${word}`);
        console.log("───────────────────────────────────");

        if (runSyllable) {
            console.log(`Sílabas: ${syllables.join(" - ")}`);
        }

        if (runTonic) {
            const tonicNumber = tonic(syllables);
            const tonicSyllableText = syllables[syllables.length - tonicNumber];
            let tipoSilaba: string;
            if (tonicNumber === 1) {
                tipoSilaba = "oxítona";
            } else if (tonicNumber === 2) {
                tipoSilaba = "paroxítona";
            } else if (tonicNumber === 3) {
                tipoSilaba = "proparoxítona";
            } else {
                tipoSilaba = "???";
            }
            console.log(`Sílaba tônica: '${tonicSyllableText}' (${tipoSilaba} #${tonicNumber})`);
        }
        console.log("───────────────────────────────────");
        console.log(""); // Add a newline for better visual separation
    } else {
        // Original non-full output behavior
        if (runSyllable) {
            console.log(syllables.join("-"));
        }

        if (runTonic) {
            const tonicNumber = tonic(syllables);
            console.log(tonicNumber);
        }
    }

    return 0;
}

// Start the program
process.exit(main(process.argv.slice(2)));
