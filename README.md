# separador-silabas
Separador de sílabas e identificador de sílabas tônicas em língua portuguesa usando regex
# Como usar
## javascript
Na sua página html, inclua no header:
```html
<script src="https://gigiodelchiaro.github.io/separador-silabas/syllable.js"></script> <!--para separar silabas-->
<script src="https://gigiodelchiaro.github.io/separador-silabas/tonic.js"></script> <!--para marcar silabas tônicas-->
```
```javascript
separarTexto("texto como um todo") // retorna: "tex-to co-mo um to-do"

tonica(["a", "bó", "bo", "ra"]) // retorna 3
tonica(["ca", "sa"]) // retorna 2
tonica(["a", "qui"]) // retorna 1
```
Dica! Para usar os dois programas juntos, utilize este código
```javascript
let silabas = separarTexto(palavra).split("-");
let numeroTonica = tonica(silabas);
```
## python
Instale as dependencias:
```
pip install -r requirements.txt
```
Execute "syllables.py"
# Eventuais problemas
Separação incorreta, falta de tratamento de erro, sugestões, etc. -> Abra um issue em https://github.com/gigiodelchiaro/separador-silabas/issues
