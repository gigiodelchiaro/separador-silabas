
# Separador de Sílabas e Identificador de Tônica

Este projeto oferece uma solução robusta e de alta precisão para a separação silábica e identificação da sílaba tônica em palavras da língua portuguesa. Com um núcleo lógico implementado em Typescript, a ferramenta garante performance e portabilidade.

## Destaques da Versão 2.0 (Typescript)

A versão 2.0 representa uma reescrita completa da lógica em Typescript, o que resultou em melhorias significativas de precisão, validadas através de comparações com o dicionário de separação silábica do [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org/index.php?action=syllables&act=list).

-   **Precisão da Separação Silábica:** **99.73%** (anteriormente 94.58%)
-   **Precisão da Identificação da Sílaba Tônica:** **99.91%** (anteriormente 92.97%)

## Estrutura do Repositório

-   `syllable.ts`: Lógica principal para a separação de sílabas.
-   `tonic.ts`: Lógica principal para a identificação da sílaba tônica.

---

## Como Utilizar

### Como CLI

Para utilizar a ferramenta via linha de comando, você pode executar o `index.ts` diretamente. Certifique-se de ter o `bun` instalado.

```bash
bun run index.ts --word <palavra> [--tonic] [--syllable] [--full]
```

**Opções:**

*   `--word <palavra>`: A palavra a ser analisada (obrigatório).
*   `--tonic`: Executa apenas a análise da sílaba tônica.
*   `--syllable`: Executa apenas a separação silábica.
*   `--full`: Habilita o modo de saída completo, com informações detalhadas e formatadas.

**Exemplos:**

```bash
# Separar sílabas e identificar tônica de "exemplo" (saída padrão)
bun run index.ts --word exemplo

# Apenas separar sílabas de "computador"
bun run index.ts --word computador --syllable

# Apenas identificar a tônica de "paralelepípedo"
bun run index.ts --word paralelepípedo --tonic

# Saída completa para "caminhão"
bun run index.ts --word caminhão --full
```

### Como Utilizar em um Site Estático

Para integrar a lógica de separação silábica e identificação de tônica em um site estático, você pode compilar os arquivos Typescript para Javascript e incluí-los em seu projeto.

1.  **Compilar os arquivos:**
    Certifique-se de ter o TypeScript instalado (`npm install -g typescript` ou `bun install -g typescript`).
    No diretório raiz do projeto, execute:
    ```bash
    tsc
    ```
    Isso irá gerar os arquivos Javascript (`.js`) na pasta de saída configurada no `tsconfig.json` (geralmente `dist/`).

2.  **Utilizar as funções:**
    Após a compilação, você pode incluir os arquivos Javascript gerados (`dist/syllable.js` e `dist/tonic.js`) em seu HTML. As funções `syllable` e `tonic` estarão disponíveis globalmente (assumindo uma configuração de módulo compatível para navegadores, como UMD ou System, ou ESNext se estiver usando módulos no navegador).

    Exemplo de uso em JavaScript:

    ```javascript
    // Certifique-se de que syllable.js e tonic.js foram carregados no HTML
    // Ex: <script src="dist/syllable.js"></script>
    // Ex: <script src="dist/tonic.js"></script>

    const word = "exemplo";
    const syllables = syllable(word).split('@');
    const tonicNumber = tonic(syllables);
    const tonicSyllableText = syllables[syllables.length - tonicNumber];

    console.log(`Sílabas: ${syllables.join(' - ')}`);
    console.log(`Sílaba Tônica: '${tonicSyllableText}' (posição: #${tonicNumber})`);
    ```

    **Nota:** Dependendo da sua configuração de módulo (ESM, CommonJS), você pode precisar ajustar a forma como importa e utiliza as funções. Para uso em navegadores, certifique-se de que o `tsconfig.json` esteja configurado para um `target` compatível (ex: `ES2015` ou superior) e `module` como `UMD` ou `System` se precisar de compatibilidade global, ou `ESNext` se estiver usando módulos no navegador.

---

## Problemas e Sugestões

Encontrou uma separação incorreta, falta de tratamento de erro ou tem alguma sugestão? Por favor, abra uma issue no repositório oficial:
[https://github.com/gigiodelchiaro/separador-silabas/issues](https://github.com/gigiodelchiaro/separador-silabas/issues)