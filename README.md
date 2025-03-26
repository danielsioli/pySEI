# pySEI
Atualizado para interagir com o SEI 4.0

Pacote para interagir com o SEI - Sistema Eletrônico de Informação. O pacote usa Selenium com o chromedriver ou Ms Edge.
O chromedriver pode ser obtido em https://chromedriver.chromium.org/downloads
O Ms Edge Driver pode ser obtido em https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

## Install 

```
pip install pySEI
```

## Use
Importar pacote
```
from pySEI import Sei
```
Iniciar navegador
```
sei = Sei(headless=False)
```
Iniciar navegador headless
```
sei = Sei()
```
Especificar o caminho para o chromedriver
```
sei = Sei(executable_path='chromedriver')
```
Entrar na página do SEI
```
sei.start_driver(url='http://sei.anatel.gov.br', usuario=usuario, senha=senha)
```
Ir para um processo
```
sei.go_to(numero_sei=numero_sei)
```
Verificar se um processo está aberto em uma área
```
is_aberto,mensagem = sei.is_processo_aberto(processo=processo,area=area)
```
Verificar se um processo está anexado a outro
```
processo_anexador = sei.get_processo_anexador(processo=processo)
```
Trocar área do usuário
```
is_area_trocada = sei.seleciona_area(area=area)
```
Clicar em um botão do processo ou documento
```
is_botao_clicado = sei.clicar_botao(botao=botao)
```
Verificar se o processo está sobrestado
```
is_sobrestado,mensagem_sobrestamento = sei.is_sobrestado(processo=processo)
```
Verificar se o processo está sobrestado em uma área
```
is_sobrestado,is_na_area = sei.is_sobrestado(processo=processo, area=area)
```
Sobrestar processo na área atual
```
is_sobrestado = sei.sobrestar_processo(motivo='Quero sobrestar', processo=processo)
```
Remover sobrestamento do processo na área atual
```
sobrestamento_removido = sei.remover_sobrestamento(processo=processo)
```
Fechar a janela de alerta
```
mensagem_alerta = sei.fechar_alerta()
```
Publicar apenas no Boletim de Serviço
```
is_publicado = sei.publicar(documento=documento
    ,resumo_ementa=resumo_ementa, data_disponibilizacao='21/01/2021')
```
Publicar no Boletim de Serviço e no DOU
```
is_publicado = sei.publicar(documento=documento
    ,resumo_ementa=resumo_ementa, data_disponibilizacao='21/01/2021'
    , dou=dou, secao=secao, pagina=pagina)
```
Obter conteúdo HTML de documento
```
try:
    conteudo_documento = sei.get_conteudo_documento(documento=documento)
except:
    print('Conteúdo não encontrado')
```

Incluir documento em bloco de assinatura
```
sei.incluir_em_bloco(bloco=bloco, documento=documento)
```

Fechar o navegador
```
sei.close()
```