const strongAccents = 'áéíóúàèìòùâêîôûÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ';
const weakAccents = 'ãẽĩõũÃẼĨÕŨ';
function tonica(wordSeparated) {
    if (wordSeparated.length === 1) {
        return 1;
    }

    // Check for strong accents
    for (let i = wordSeparated.length - 1; i >= 0; i--) {
        if ([...wordSeparated[i]].some(char => strongAccents.includes(char))) {
            return wordSeparated.length - i;
        }
    }

    // Check for weak accents
    for (let i = wordSeparated.length - 1; i >= 0; i--) {
        if ([...wordSeparated[i]].some(char => weakAccents.includes(char))) {
            return wordSeparated.length - i;
        }
    }

    const lastSyllable = wordSeparated[wordSeparated.length - 1];
    const regex = /(i(s)?|u|z|im|us|r|l|x|n|um(s)?|ps|om|on(s)?)(\W+)?$/;

    // Check for special case
    if (regex.test(lastSyllable)) {
        return 1;
    }

    return 2;
}
console.log("Identificador de sílabas tônicas carregado com sucesso!");