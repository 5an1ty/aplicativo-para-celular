# Bob Esponja Snake — Android

APK autônomo, offline, com músicas incluídas e sem permissões Android. O jogo HTML/Canvas original roda na WebView do sistema com aceleração de hardware. O ícone é uma ilustração própria do Bob Esponja. Não é um aplicativo oficial da Nickelodeon.

## Instalar

Transfira `build/Bob-Esponja-Snake.apk` para o celular, abra o arquivo e permita a instalação por esse navegador ou gerenciador de arquivos quando o Android solicitar. Não precisa de loja, conta ou conexão para jogar.

Requer Android 6.0 ou superior e Android System WebView/Chrome atualizado. O APK não contém bibliotecas nativas específicas de arquitetura, atendendo a ARM, ARM64 e x86. Não é possível garantir suporte a todo aparelho, especialmente WebViews antigos, dispositivos sem WebView e celulares administrados que bloqueiam instalação de APKs.

O botão Voltar pausa a partida; ao pressionar novamente, retorna ao menu. No menu, pede confirmação para sair. Ao trocar de aplicativo, a partida é pausada. Recordes e preferências são armazenados localmente; desinstalar ou limpar os dados os apaga. A partida em andamento não é restaurada se o sistema encerrar o processo.

## Compilar

Pré-requisitos: Java 21 (runtime basta), Python 3, `zip`, acesso HTTPS ao repositório Android do Google e Maven Central. Não precisa de Gradle, Android Studio ou NDK.

```sh
cd /workspace/aplicativo-para-celular/android
python3 setup-tools.py
./build.sh
```

Ferramentas baixadas com verificação de checksum. Por padrão ficam em `/workspace/android-tools`; `ANDROID_BUILD_TOOLS`, `ANDROID_JAR` e `ECJ_JAR` permitem indicar outras localizações para a compilação. `BOB_ANDROID_TOOLS` muda a pasta de download do instalador.

A compilação copia os arquivos de `../megabrain`, remove a importação remota de fontes somente dessa cópia, compila o contêiner Java, gera DEX, alinha e assina o APK. O código web original permanece inalterado. Reexecute `build.sh` após mudanças no jogo.

A chave de assinatura local fica em `/workspace/android-signing/bob-snake.jks`, fora do Git. Preserve essa chave de maneira privada: atualizações instaladas sobre esta versão precisam da mesma assinatura. `BOB_SNAKE_KEYSTORE` permite escolher outra chave compatível com o alias e senha configurados em `build.sh`. A senha padrão é apenas uma conveniência de compilação local; a proteção da chave depende do acesso ao arquivo. Este pacote é para instalação direta, não uma publicação em loja.

## Validação realizada

- Compilação Java/DEX e empacotamento Android API 35; mínimo API 23.
- Assinaturas APK v1, v2 e v3 verificadas com `apksigner`.
- Alinhamento de arquivos verificado com `zipalign`.
- Conteúdo extraído diretamente do APK exercitado no Chromium mobile, com acesso externo bloqueado: partida, movimento, pausa, menu, tutorial batalha e áudio.

Para repetir o teste de conteúdo (requer Python Playwright e Chromium):

```sh
python3 smoke-apk.py
```

Não houve instalação em aparelho físico ou emulador Android nesta máquina. O teste Chromium verifica o jogo empacotado; não comprova o comportamento nativo de todos os modelos Android.

## Versão 1.1 — interface mobile

Menu e partida com ilustrações vetoriais locais, tipografia Nunito incluída com licença OFL, painéis de madeira, botões em relevo e controles separados do mapa. O layout se adapta à orientação e preserva o número de células durante a partida. O modal de pausa cobre também os controles em telas pequenas.

A WebView serve SVG e fontes locais com os tipos MIME correspondentes. `versionCode=2`, `versionName=1.1`, assinado com a mesma chave da primeira versão.

Validação adicional: `python3 test-ui.py`, com o conteúdo de `megabrain` servido na porta 8010. Cobertura: 390×844, 360×640, 320×568, 412×915, 844×390 e 1280×900; ausência de sobreposição entre mapa/direcional; tela cheia; pontuação por dificuldade; poderes; pausa; seleção de personagens; tutorial; habilidade de Sandy. Nenhuma alteração nas regras, IA, colisões, probabilidades, pontuação ou duração dos poderes.

O alerta do Defender relatado na versão 1.0 não foi diagnosticado; esta atualização não é uma correção antimalware nem foi validada pelo Defender.
