
// Function to load JSON rules file
async function loadRules(filePath) {
    const response = await fetch(filePath);
    return await response.json();
}
var rules;
var divisor;
function definirSeparador(valor){
    divisor = valor;
    console.log("Separador mudado para: '" + divisor + "'");
}
async function reload() {
    const rulesFile = "https://gigiodelchiaro.github.io/separador-silabas/rules.json"; // Update to your JSON file path
    rules = await loadRules(rulesFile);
    // Load the rules from the JSON file
    const digrafos = rules.digrafos;


    const vogais = rules.vogais_fortes + rules.vogais_fracas;
    const consoantes = rules.consoantes_fortes + rules.consoantes_l_r + rules.consoantes_nasais + rules.consoantes_s;

    const letras = vogais + consoantes;
    rules.padroes.forEach(pattern => {
        // Replace placeholders in regex
        pattern.regex = pattern.regex
            .replaceAll("{consoantes_fortes}", rules.consoantes_fortes)
            .replaceAll("{consoantes_l_r}", rules.consoantes_l_r)
            .replaceAll("{consoantes_nasais}", rules.consoantes_nasais)
            .replaceAll("{consoantes_s}", rules.consoantes_s)
            .replaceAll("{vogais}",vogais)
            .replaceAll("{vogais_fortes}", rules.vogais_fortes)
            .replaceAll("{digrafos}", digrafos)
            .replaceAll("{letras}", letras)
            .replaceAll("{\\\\1}", "\\1")
            .replaceAll("{\\1}", "$1")
            .replaceAll("{\\2}", "$2")
            .replaceAll("{\\3}", "$3");

        pattern.regex = new RegExp(pattern.regex, 'gm'); // Add 'g' or other flags as needed

        // Replace placeholders in replacement string
        pattern.sub = pattern.sub
            .replaceAll("{\\1}", "$1")
            .replaceAll("{\\2}", "$2")
            .replaceAll("{\\3}", "$3");
    });
    console.log("Separador de silabas carregado com sucesso!");
}
document.addEventListener("DOMContentLoaded", async () => {
    reload();
    definirSeparador("-"); // Valor padrao
});
// Function to apply rules to the input text
function separarTexto(text) {
    text = text.replaceAll("@", "");
    rules.padroes.forEach(pattern => {
        const regex = pattern.regex;
        text = text.replaceAll(regex, pattern.sub);
    });
    return text.replaceAll("@", divisor);
}
