
# Separador de Sílabas e Identificador de Tônica

Este projeto oferece uma solução robusta e de alta precisão para a separação silábica e identificação da sílaba tônica em palavras da língua portuguesa. Com um núcleo lógico implementado em Lua, a ferramenta garante performance e portabilidade.

## Destaques da Versão 2.0 (Lua Core)

A versão 2.0 representa uma reescrita completa da lógica em Lua, o que resultou em melhorias significativas de precisão, validadas através de comparações com o dicionário de separação silábrica do [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org/index.php?action=syllables&act=list).

-   **Precisão da Separação Silábica:** **99.65%** (anteriormente 94.58%)
-   **Precisão da Identificação da Sílaba Tônica:** **99.89%** (anteriormente 92.97%)

## Estrutura do Repositório

-   `syllable.lua`: Lógica principal para a separação de sílabas.
-   `tonic.lua`: Lógica principal para a identificação da sílaba tônica.

---

## Como Utilizar

Você pode usar as funcionalidades deste projeto de duas maneiras: diretamente via linha de comando com um interpretador Lua ou integrado a uma página web com JavaScript.

### 1. Uso via Linha de Comando (Lua)

Execute os scripts `syllable.lua` e `tonic.lua` diretamente no seu terminal.

#### **Separando Sílabas (`syllable.lua`)**

Use o script `syllable.lua` com a flag `--word` para dividir uma palavra em sílabas.

**Comando:**
```bash
lua syllable.lua --word <palavra>
```

**Exemplo:**
```bash
lua syllable.lua --word desenvolvimento
```

**Saída:**
```
de-sen-vol-vi-men-to
```

#### **Identificando a Sílaba Tônica (`tonic.lua`)**

Use o script `tonic.lua` com a flag `--word` para encontrar a posição da sílaba tônica.

**Comando:**
```bash
lua tonic.lua --word <palavra>
```

**Interpretação da Saída:**
O script retorna um número que classifica a palavra quanto à tonicidade:
*   **1:** Oxítona (última sílaba tônica)
*   **2:** Paroxítona (penúltima sílaba tônica)
*   **3:** Proparoxítona (antepenúltima sílaba tônica)

**Exemplos:**
```bash
# Palavra Oxítona
lua tonic.lua --word café
# Saída: 1

# Palavra Paroxítona
lua tonic.lua --word palavra
# Saída: 2

# Palavra Proparoxítona
lua tonic.lua --word sílaba
# Saída: 3
```

---

### 2. Uso em uma Página Web (JavaScript)

É possível executar os scripts `.lua` diretamente no navegador usando a biblioteca [Fengari](https://github.com/fengari-lua/fengari), sem a necessidade de um servidor de backend.

#### **Configuração**

Para integrar o separador de sílabas ao seu site, adicione o seguinte código ao `<head>` do seu arquivo HTML.

```html
<!-- 1. Carregue a biblioteca Fengari -->
<script src="https://cdn.jsdelivr.net/npm/fengari-web@0.1.4/dist/fengari-web.js" type="text/javascript"></script>

<!-- 2. Carregue seus scripts .lua (coloque-os na mesma pasta do seu HTML) -->
<script src="syllable.lua" type="application/lua" async></script>
<script src="tonic.lua" type="application/lua" async></script>

<!-- 3. Crie a "ponte" de comunicação entre Lua e JavaScript -->
<script type="application/lua">
    local js = require "js"
    local separador_atual = '-' -- Define o separador padrão

    -- Cria a função 'definirSeparador' para ser usada no JS
    js.global.definirSeparador = function(novo_separador)
        if novo_separador and type(novo_separador) == "string" then
            separador_atual = novo_separador
        end
    end

    -- Cria uma função JS global 'separarTexto' que chama a função Lua 'syllabify'
    js.global.separarTexto = function(texto)
        if not texto or texto:gmatch("%S")() == nil then return texto end
        
        local palavras = {}
        for palavra in texto:gmatch("%S+") do
            local silabas_str = syllabify(palavra) -- Lua retorna sílabas com '@'
            table.insert(palavras, silabas_str:gsub('@', separador_atual)) -- Troca '@' pelo separador definido
        end
        return table.concat(palavras, ' ')
    end

    -- Expõe a função 'tonic' do Lua diretamente para o JavaScript
    js.global.tonica = tonic
</script>
```

#### **Modo de Uso em JavaScript**

Após a configuração, você pode chamar as funções `definirSeparador()`, `separarTexto()` e `tonica()` em qualquer script da sua página.

*Observação: Como os scripts são carregados de forma assíncrona, certifique-se de que a página esteja completamente carregada antes de chamar as funções.*

**Exemplos:**

```javascript
// Opcional: Define um separador customizado. O padrão é "-".
definirSeparador("_");

// Separa as sílabas de uma palavra ou texto com o separador definido.
separarTexto("texto como um todo"); // retorna: "tex_to co_mo um to_do"


// Identifica a sílaba tônica a partir de um array de sílabas.
tonica(["a", "bó", "bo", "ra"]); // retorna: 3 (Proparoxítona)
tonica(["ca", "sa"]); // retorna: 2 (Paroxítona)
tonica(["a", "qui"]); // retorna: 1 (Oxítona)
```

**Dica!** Para usar as duas funções em conjunto, utilize este código. Lembre-se de usar o mesmo separador no `split()` que você definiu.

```javascript
let palavra = "computador";
let meuSeparador = "-"; // Pode ser qualquer string: "_", ".", etc.

// Define o separador a ser usado
definirSeparador(meuSeparador);

// 1. Usa separarTexto() e split() para criar o array de sílabas
let silabas = separarTexto(palavra).split(meuSeparador); // Retorna: ["com", "pu", "ta", "dor"]

// 2. Usa o array de sílabas para identificar a tônica
let numeroTonica = tonica(silabas); // Retorna: 1
```

## Problemas e Sugestões

Encontrou uma separação incorreta, falta de tratamento de erro ou tem alguma sugestão? Por favor, abra uma issue no repositório oficial:
[https://github.com/gigiodelchiaro/separador-silabas/issues](https://github.com/gigiodelchiaro/separador-silabas/issues)