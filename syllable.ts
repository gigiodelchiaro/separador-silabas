// @filename: syllable.ts
/**
 * Separates the word using pt-br standard
 *
 * @param word The word to be separated
 * @returns The word separated by '@' characters
 */

let VOGAIS_FRACAS = "iouïöüy"
let VOGAIS_FORTES = "aeáéóàèòãẽõâêôäëöíúìùĩũîû"
let CONSOANTES_FORTES = "bcdfgjkpqtvwxyzç"
let CONSOANTES_LIQUIDAS = "lr"
let CONSOANTES_NASAIS = "mn"


let VOGAIS = VOGAIS_FRACAS + VOGAIS_FORTES + "e"
let CONSOANTES = CONSOANTES_FORTES + CONSOANTES_LIQUIDAS + CONSOANTES_NASAIS + "s"
let CONSOANTES_FRACAS = CONSOANTES_LIQUIDAS + CONSOANTES_NASAIS + "s"
let LETRAS = VOGAIS + CONSOANTES

const DIGRAFOS = ["ch", "lh", "nh", "gu", "qu"];

function is_digraph(text: string, pos: number): [boolean, string | null] {
    for (const digraph of DIGRAFOS) {
        if (text.substring(pos, pos + digraph.length) === digraph) {
            return [true, digraph];
        }
    }
    return [false, null];
}

function text_to_chars(text: string): string[] {
    const chars: string[] = [];
    let i = 0;
    while (i < text.length) {
        const [isDig, digraph] = is_digraph(text, i);
        if (isDig) {
            chars.push(digraph!);
            i += digraph!.length;
        } else {
            // Handle UTF-8 characters (TypeScript strings are UTF-16, but this handles common cases)
            // For full Unicode grapheme cluster support, a library might be needed.
            const char = text.charAt(i);
            chars.push(char);
            i += char.length;
        }
    }
    return chars;
}

function char_in_set(char: string, set_spec: string): boolean {
    return set_spec.includes(char);
}

function match_pattern(chars: string[], pos: number, pattern: string[]): boolean {
    if (pos < 0 || pos + pattern.length > chars.length) {
        return false;
    }

    for (let i = 0; i < pattern.length; i++) {
        const pattern_char = pattern[i]!;
        const actual_char = chars[pos + i]!;

        if (pattern_char === "@") {
            if (actual_char !== "@") {
                return false;
            }
        } else if (!char_in_set(actual_char, pattern_char)) {
            return false;
        }
    }
    return true;
}

interface Rule {
    position: number;
    pattern: string[];
}

function create_rule(chars: string[], index: number): string[] {
    const newChars = [...chars];
    newChars.splice(index, 0, "@");
    return newChars;
}

function cleanup_rule(chars: string[], index: number): string[] {
    const newChars = [...chars];
    newChars.splice(index, 1);
    return newChars;
}

const SYLLABIFICATION_RULES: Rule[] = [
    { position: 1, pattern: [VOGAIS, "o"] },
    { position: 1, pattern: [VOGAIS_FRACAS, VOGAIS_FORTES] },
    { position: 1, pattern: ["aeí", VOGAIS_FORTES] },
    { position: 0, pattern: [CONSOANTES_FORTES] },
    { position: 0, pattern: [CONSOANTES_FRACAS, VOGAIS] },
    { position: 0, pattern: ["bd", "s"] },
];

const CLEANUP_RULES: Rule[] = [
    { position: 2, pattern: [CONSOANTES_FORTES, "@", CONSOANTES_LIQUIDAS] },
    { position: 1, pattern: ["@", CONSOANTES_FORTES, "@", CONSOANTES_NASAIS + "s"] },
    { position: 1, pattern: ["@", CONSOANTES_FORTES, "@", CONSOANTES_FORTES] },
    { position: 2, pattern: ["ã", "@", "o"] },
];

function syllabify_letters(word: string): string {
    const lowerWord = word.toLowerCase();
    let chars: string[] = text_to_chars(lowerWord);
    const exceptions: string[] = ["ao", "aos", "caos"];
    for (let i = 0; i < exceptions.length; i++) {
        if (lowerWord == exceptions[i]) {
            return word
        }
    }

    if (chars.length <= 1) {
        return word;
    }

    // Apply syllabification rules
    const separators: { [key: number]: boolean } = {};
    for (let i = 0; i < chars.length - 1; i++) {
        for (const rule of SYLLABIFICATION_RULES) {
            if (match_pattern(chars, i, rule.pattern)) {
                const insert_pos = i + rule.position;
                if (insert_pos >= 0 && insert_pos <= chars.length) {
                    separators[insert_pos] = true;
                    break; // Apply first matching rule at each position
                }
            }
        }
    }

    // Insert separators
    let result_chars: string[] = [];
    for (let i = 0; i < chars.length; i++) {
        result_chars.push(chars[i]!);
        if (separators[i + 1] && i < chars.length - 1) {
            result_chars.push("@");
        }
    }

    // Apply cleanup rules
    let processedChars = result_chars;
    for (const rule of CLEANUP_RULES) {
        // Iterate from the end to avoid issues with changing array length
        for (let i = processedChars.length - rule.pattern.length; i >= 0; i--) {
            if (match_pattern(processedChars, i, rule.pattern)) {
                let atIndexInPattern = -1;
                for(let k = 0; k < rule.pattern.length; k++) {
                    if (rule.pattern[k] === '@') {
                        atIndexInPattern = k;
                        break;
                    }
                }
                if (atIndexInPattern !== -1) {
                    processedChars = cleanup_rule(processedChars, i + atIndexInPattern);
                }
            }
        }
    }

    // Post-processing (as new rules or direct string manipulations)
    let finalResult = processedChars.join("");
    for (const digraph of DIGRAFOS) {
        finalResult = finalResult.replace(new RegExp(digraph, "g"), "@" + digraph);
    }
    finalResult = finalResult.replace(/[gq]@u/g, "gu");
    finalResult = finalResult.replace(/([aeou])(i[nmrlz])$/, "$1@$2");
    finalResult = finalResult.replace(/@bs@/g, "bs@");
    finalResult = finalResult.replace(/@d@q/g, "d@q");
    finalResult = finalResult.replace(/([aei])([oui])([mn])/g, "$1@$2$3");
    finalResult = finalResult.replace(/([aeo])in/g, "$1@in");
    finalResult = finalResult.replace(/([aeou])i@nh/g, "$1@i@nh");
    finalResult = finalResult.replace(/([gq])u@([ei])/g, "$1u$2");
    
    finalResult = finalResult.replace(/@+/g, "@"); 
    finalResult = finalResult.replace(/^@/g, ""); 
    
    return finalResult;
}

export default function syllable(word: string): string {
    const originalChars = text_to_chars(word);
    const letterChars: string[] = [];

    originalChars.forEach((char) => {
        if (char_in_set(char.toLowerCase(), LETRAS)) {
            letterChars.push(char);
        }
    });

    if (letterChars.length === 0) {
        return word;
    }

    const letterWord = letterChars.join('');
    const syllabifiedLetterWord = syllabify_letters(letterWord);
    const syllabifiedLetterChars = text_to_chars(syllabifiedLetterWord);

    const finalChars: string[] = [];
    let syllabifiedCursor = 0;

    for (const originalChar of originalChars) {
        if (char_in_set(originalChar.toLowerCase(), LETRAS)) {
            while (
                syllabifiedCursor < syllabifiedLetterChars.length &&
                (syllabifiedLetterChars[syllabifiedCursor] === '@' || syllabifiedLetterChars[syllabifiedCursor] === '-')
            ) {
                finalChars.push(syllabifiedLetterChars[syllabifiedCursor]);
                syllabifiedCursor++;
            }

            finalChars.push(originalChar);

            if (
                syllabifiedCursor < syllabifiedLetterChars.length &&
                syllabifiedLetterChars[syllabifiedCursor].toLowerCase() === originalChar.toLowerCase()
            ) {
                syllabifiedCursor++;
            }
        } else {
            finalChars.push(originalChar);
        }
    }

    while (syllabifiedCursor < syllabifiedLetterChars.length) {
        const char = syllabifiedLetterChars[syllabifiedCursor];
        if (char === '@' || char === '-') {
            finalChars.push(char);
        }
        syllabifiedCursor++;
    }

    let finalResult = finalChars.join('');
    finalResult = finalResult.replace(/-/g, "-@");
    finalResult = finalResult.replace(/@+/g, "@");
    
    return finalResult;
}