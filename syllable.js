
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
    reload();
}
async function reload() {
    // Load the rules from the JSON file
    const rulesFile = "https://raw.githubusercontent.com/gigiodelchiaro/separador-silabas/refs/heads/main/rules.json"; // Update to your JSON file path
    rules = await loadRules(rulesFile);
    const vogais = rules.vogais_fortes + rules.vogais_fracas;
    const digrafos = rules.digrafos;

    rules.padroes.forEach(pattern => {
        // Replace placeholders in regex
        pattern.regex = pattern.regex
            .replace("{consoantes_fortes}", rules.consoantes_fortes)
            .replace("{consoantes_fracas}", rules.consoantes_fracas)
            .replace("{vogais}",vogais)
            .replace("{vogais_fortes}", rules.vogais_fortes)
            .replace("{digrafos}", digrafos)
            .replace("{divisor}", divisor);

        // Replace placeholders in replacement string
        pattern.replace = pattern.replace
            .replace("{divisor}", divisor)
            .replace("{\\1}", "$1")
            .replace("{\\2}", "$2")
            .replace("{\\3}", "$3")
    });
    console.log("Separador de silabas carregado com sucesso!");
}
document.addEventListener("DOMContentLoaded", async () => {
    
    definirSeparador("-"); // Valor padrao
});
// Function to apply rules to the input text
function separarTexto(text) {
    rules.padroes.forEach(pattern => {
        const regex = new RegExp(pattern.regex, 'g');
        text = text.replace(regex, pattern.replace);
    });
    return text;
}
