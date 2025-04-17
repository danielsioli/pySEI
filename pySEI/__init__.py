from selenium import webdriver
from selenium import __version__ as selenium_version
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from re import search, sub
from getpass import getpass
#from msedge.selenium_tools import EdgeOptions
#from msedge.selenium_tools import Edge
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager as MsDriverManager
import configparser
import pandas as pd
import os 
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

class Sei:

    __area_inicial = None
    __windows_before = 0
    __windows_after = 0

    def __init__(self, headless: bool = False, executable_path: str = 'chromedriver', sei_versao: int = 4, download_path = None):
        self.config = configparser.ConfigParser()
        self.diretorio = None
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with pkg_resources.open_text(package='pySEI', resource='config.ini') as f:
            self.config.read_file(f)
        self.sei = 'sei' + str(sei_versao)
        if 'chromedriver' in executable_path:
            chrome_options = Options()
            chrome_options.add_argument('--enable-javascript')
            chrome_options.add_argument('--window-size=1440,900')
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--proxy-server='direct://'")
            chrome_options.add_argument("--proxy-bypass-list=*")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--ignore-certificate-errors')
            if headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-software-rasterizer')
            if download_path:
                self.diretorio = download_path
                prefs = {'download.default_directory': download_path}
            else:
                self.diretorio = dir_path
                prefs = {'download.default_directory': dir_path}
            prefs['download.prompt_for_download'] = False
            prefs['download.directory_upgrade'] = True
            prefs['plugins.always_open_pdf_externally'] = True
            chrome_options.add_experimental_option("prefs",prefs)
            executable_path = ChromeDriverManager().install()
            service = Service(executable_path=executable_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            #self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
        #elif 'msedgedriver' in executable_path:
        #    edge_options = EdgeOptions()
        #    edge_options.use_chromium = True
        #    edge_options.add_argument('enable-javascript')
        #    edge_options.add_argument('window-size=1440,900')
        #    edge_options.add_argument("disable-extensions")
        #    edge_options.add_argument("proxy-server='direct://'")
        #    edge_options.add_argument("proxy-bypass-list=*")
        #    edge_options.add_argument("start-maximized")
        #    edge_options.add_argument('disable-dev-shm-usage')
        #    edge_options.add_argument('no-sandbox')
        #    edge_options.add_argument('ignore-certificate-errors')
        #    if headless:
        #        edge_options.add_argument('headless')
        #        edge_options.add_argument('disable-gpu')
        #    self.driver = Edge(executable_path=MsDriverManager.install(), options=edge_options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start_driver(self, url: str, usuario:str = None, senha:str = None, chave: str = None, orgao: str = 'ANATEL'):

        if usuario == None:
            usuario = input('Digite o usuário: ')
        if senha == None:
            senha = getpass('Digite a senha: ')

        self.driver.get(url)

        usuario_field = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'usuario_textfield'))))

        senha_field = self.driver.find_element(By.ID, self.config.get(self.sei, 'senha_textfield'))
        botao_acessar = self.driver.find_element(By.ID, self.config.get(self.sei, 'acessar_botao'))

        usuario_field.clear()
        usuario_field.send_keys(usuario)
        senha_field.clear()
        senha_field.send_keys(senha)
        try:
            orgao_drop_down = Select(WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'seleciona_orgao')))))
            orgao_drop_down.select_by_visible_text(orgao)
        except:
            None
        #selOrgao
        botao_acessar.click()
        #txtCodigoAcesso
        try:
            chave_field = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'txtCodigoAcesso')))
            chave_field.clear()
            chave_field.send_keys(chave)
            #sbmValidar
            self.driver.find_element(By.ID, 'sbmValidar').click()
        except:
            None
        alerta = self.fechar_alerta()
        if alerta:
            raise Exception(alerta)  # usuário ou senha inválido
        self.__area_inicial = self.get_area()

    def go_to(self, numero_sei: str):
        if self.__windows_after > self.__windows_before:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[self.__windows_before - 1])
        self.driver.switch_to.default_content()
        pesquisa = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'pesquisa_textfield'))))
        pesquisa.clear()
        pesquisa.send_keys(str(numero_sei))
        formPesquisaRapida = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'pesquisa_form'))))
        self.__windows_before = len(self.driver.window_handles)
        formPesquisaRapida.submit()
        self.__windows_after = len(self.driver.window_handles)
        if self.__windows_after > self.__windows_before:
            self.driver.switch_to.window(self.driver.window_handles[self.__windows_after - 1])
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'pesquisa_textfield'))))

    def is_processo_aberto(self, area:str = None, processo: str = None) -> tuple[bool, str]:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            informacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'documento_informacao'))))
            mensagem = informacao.text
            aberto = 'aberto' in mensagem
            if area:
                regex = '(?im)^(.*)(' + area + ')[^0-9a-z](.*)$'
                matches = search(regex, mensagem)
                if matches:
                    aberto = True
                else:
                    aberto = False
            self.driver.switch_to.default_content()
        except:
            aberto = None
            mensagem = 'Impossível abrir mensagem do processo'
        return aberto, mensagem

    def get_processo_anexador(self, processo: str = None) -> str:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'documento_informacao'))))
        procAnex = None
        if 'Processo anexado ao processo' in informacao.text:
            processoAnexador = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, r'//*[@id="' + self.config.get(self.sei, 'documento_informacao') + r'"]/div/a')))
            procAnex = processoAnexador.text
        self.driver.switch_to.default_content()
        return procAnex

    def get_area(self) -> str:
        self.driver.switch_to.default_content()
        areas_listbox = self.driver.find_element(By.ID, self.config.get(self.sei, 'areas_listbox'))
        if areas_listbox.tag_name == 'select':
            select = Select(areas_listbox)
            return select.all_selected_options[0].text
        else:
            return areas_listbox.get_attribute('innerHTML')

    def seleciona_area(self, area: str) -> bool:
        self.driver.switch_to.default_content()
        areas_listbox = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
            (By.ID, self.config.get(self.sei, 'areas_listbox'))))
        if areas_listbox.tag_name == 'select':
            select = Select(areas_listbox)
            all_selected_options = select.all_selected_options
            for option in all_selected_options:
                if area == option.text:
                    return True

            select = Select(self.driver.find_element(By.ID, self.config.get(self.sei, 'areas_listbox')))
            options = select.options
            for option in options:
                if area == option.text:
                    select.select_by_visible_text(area)
                    Select(WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'areas_listbox')))))
                    return True
            return False
        elif areas_listbox.tag_name == 'a':
            antiga_area = areas_listbox.get_attribute('innerHTML')
            self.driver.execute_script(areas_listbox.get_attribute('onclick'), areas_listbox)
            nova_area_id = self.config.get(self.sei, 'areas_tabela')
            areas_tabela = WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located(
                (By.XPATH, f"//*[@id=\"{nova_area_id}\"]/table/tbody/tr")))
            if antiga_area == area:
                return True
            for row in areas_tabela[1:]:
                if area == row.find_element(By.XPATH, 'td[2]').text:
                    row.click()
                    break
            areas_listbox = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.ID, self.config.get(self.sei, 'areas_listbox'))))
            #print(f"area = {area}, areas_listbox.text = {areas_listbox.get_attribute('innerHTML')}")
            return area == areas_listbox.get_attribute('innerHTML')
        return False

    def clicar_botao(self, botao: str) -> bool:
        self.driver.switch_to.default_content()
        ifrConteudoVisualizacao = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'conteudo_visualizacao'))))
        self.driver.switch_to.frame(ifrConteudoVisualizacao)
        arvore = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'botoes'))))
        botoes = arvore.find_elements(By.XPATH, r'//*[@id="' + self.config.get(self.sei, 'botoes') + r'"]/a')

        for b in botoes:
            img = b.find_element(By.XPATH, 'img')
            if botao in img.get_attribute('title'):
                b.click()
                try:
                    WebDriverWait(self.driver, 1).until(EC.alert_is_present(),
                                                        'Timed out waiting for PA creation ' +
                                                        'confirmation popup to appear.')
                except:
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        None
                return True
        return False

    def fechar_alerta(self) -> str:
        alerta = None
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
                                                'Timed out waiting for PA creation ' +
                                                'confirmation popup to appear.')
            alert = self.driver.switch_to.alert
            alerta = alert.text
            alert.accept()
            self.driver.switch_to.default_content()
        except TimeoutException:
            None
        return alerta

    def set_interessados(self, processo: str, interessados:list) -> tuple[bool, str]:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Consultar/Alterar Processo'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            self.driver.execute_script('objLupaInteressados.selecionar(700,500);')
            self.driver.switch_to.default_content()
            documento_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, self.config.get(self.sei, 'documento_iframe'))))
            self.driver.switch_to.frame(documento_iframe)
            for interessado in interessados:
                campo = self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_destinatario'))
                campo.clear()
                campo.send_keys(interessado)
                self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_pesquisar')).click()
                self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_tabela_destinatario')).click()
                self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_transpor')).click()
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_fechar')).click()
            self.driver.switch_to.default_content()
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_publico')).click()
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_salvar')).click()

    def gerar_circular(self, oficio: str, destinatarios: list) -> bool:
        if oficio:
            self.go_to(oficio)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, 'divArvoreConteudo')))
        if self.clicar_botao('Gerar Circular'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
        else:
            raise(Exception('Não conseguiu clicar no botão Gerar Circular'))
        self.driver.execute_script('objLupaDestinatarios.selecionar(700,500);')
        self.driver.switch_to.default_content()
        documento_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, self.config.get(self.sei, 'documento_iframe'))))
        self.driver.switch_to.frame(documento_iframe)
        for destinatario in destinatarios:
            campo = self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_destinatario'))
            campo.clear()
            campo.send_keys(destinatario)
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_pesquisar')).click()
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_tabela_destinatario')).click()
            self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_transpor')).click()
        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_fechar')).click()
        self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_gerar_circular')).click()

    def gerar_intimacao_eletronica(self, documento: str, destinatarios: list, tipo_intimidacao: str, tipo_resposta: str, anexos: list, acesso: str):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Gerar Intimação Eletrônica'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
        else:
            raise(Exception('Não conseguiu clicar no botão Gerar Intimação Eletrônica'))
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'spnJuridica'))).click()
        #self.driver.execute_script('intimacaoTipoPessoa("J");')
        #self.driver.execute_script('objLupaJuridico.selecionar(700,500);')
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, 'imgLupaTipoProcesso'))).click()
        self.driver.switch_to.default_content()
        destinatario_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[2]/iframe')))
        self.driver.switch_to.frame(destinatario_iframe)
        for destinatario in destinatarios:
            campo = self.driver.find_element(By.ID, 'txtCnpj')
            campo.clear()
            campo.send_keys(destinatario)
            self.driver.find_element(By.ID, 'sbmPesquisar').click()
            tabela = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="divInfraAreaTabela"]/table/tbody[2]')))
            items = tabela.find_element(By.XPATH, 'tr[1]/td[4]/a').click()
            self.driver.switch_to.default_content()
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            self.driver.find_element(By.ID, 'sbmGravarUsuario').click()
            tipo_intimidacao_slt = Select(WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, 'selTipoIntimacao'))))
            tipo_intimidacao_slt.select_by_visible_text(tipo_intimidacao)
            tipo_resposta_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'selTipoResposta')))
            tipo_resposta_slt = Select(tipo_resposta_element)
            self.driver.execute_script("arguments[0].setAttribute('style',arguments[1])",tipo_resposta_element, '')
            tipo_resposta_slt.select_by_visible_text(tipo_resposta)
            lista_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div/div[3]/div[2]/div[1]/div[2]/div/div[1]/div/div')
            self.driver.execute_script("arguments[0].setAttribute('style',arguments[1])", lista_element, '')
            tipo_resposta_lista = self.driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/form/div/div[3]/div[2]/div[1]/div[2]/div/div[1]/div/div/ul/li')
            for item in tipo_resposta_lista[:-1]:
                texto = item.find_element(By.XPATH, 'label/span')
                if texto.get_attribute("innerHTML") == tipo_resposta:
                    self.driver.execute_script("arguments[0].setAttribute('class',arguments[1])", item, 'selected')
                else:
                    self.driver.execute_script("arguments[0].setAttribute('class',arguments[1])", item, '')
            self.driver.execute_script("arguments[0].setAttribute('style',arguments[1])", lista_element, 'display: none;')
            tipo_resposta_text = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div/div[3]/div[2]/div[1]/div[2]/div/div[1]/div/button/span')
            self.driver.execute_script(f"arguments[0].innerText = arguments[1]",tipo_resposta_text, tipo_resposta)
            self.driver.execute_script("arguments[0].setAttribute('style',arguments[1])",tipo_resposta_element, 'display: none;')
            if anexos:
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'lblPossuiAnexo'))).click()
                self.driver.execute_script('objLupaProtocolosIntimacao.selecionar(700,500);')
                self.driver.switch_to.default_content()
                anexo_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[2]/iframe')))
                self.driver.switch_to.frame(anexo_iframe)
                tabela = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="divInfraAreaTabela"]/table/tbody')))
                items = tabela.find_elements(By.XPATH, 'tr')
                for item in items[1:]:
                    numero_documento = item.find_element(By.XPATH, 'td[2]').text
                    if numero_documento in anexos:
                        item.find_element(By.XPATH, 'td[1]').click()
                self.driver.find_element(By.ID, 'btnTransportarSelecao').click()
                self.driver.switch_to.default_content()
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[3]'))).click()
                #tabela = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="divInfraAreaTabela"]/table/tbody[2]')))
                #items = tabela.find_element(By.XPATH, 'tr[1]/td[4]/a').click()
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
            if acesso == 'Integral':
                self.driver.find_element(By.ID, 'lblIntegral').click()
            else:
                self.driver.find_element(By.ID, 'lblParcial').click()
            self.driver.find_element(By.ID, 'sbmCadastrarMdPetIntimacao').click()
            self.driver.switch_to.default_content()
            alerta = self.fechar_alerta()
            if not alerta:
                aceite_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div[2]/iframe')))
                self.driver.switch_to.frame(aceite_iframe)
                self.driver.find_element(By.ID, 'sbmConfirmarIntimacao').click()
            self.driver.switch_to.default_content()

    def criar_documento(self, tipo: str, meta: dict, processo: str = None) -> tuple[bool, str]:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Incluir Documento'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            tipo_field = self.driver.find_element(By.ID, self.config.get(self.sei, 'tipo_documento'))
            tipo_field.clear()
            tipo_field.send_keys(tipo)
            tabela = self.driver.find_element(By.ID, self.config.get(self.sei, 'tabela_tipo_documento')).find_element(By.TAG_NAME, 'tbody')
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')
            encontrou = False
            for linha in linhas:
                style = linha.get_attribute('style')
                if 'display:none' in style:
                    continue
                if linha.text == tipo:
                    encontrou = True
                    break
            if encontrou:
                linha.click()
                self.driver.switch_to.default_content()
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, self.config.get(self.sei, 'documento_' + meta['Texto Inicial']['Opção'].replace(' ', '_'))))).click()
                campo = self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_descricao'))
                campo.clear()
                campo.send_keys(meta['Descrição'])
                campo = self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_arvore'))
                campo.clear()
                campo.send_keys(meta['Nome na Árvore'])
                destinatarios = meta['Destinatários']
                if len(destinatarios) > 1:
                    self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_publico')).click()
                    window_before = self.driver.window_handles[0]
                    self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_salvar')).click()
                    self.driver.switch_to.window(window_before)
                    self.driver.switch_to.default_content()
                    ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                    self.driver.switch_to.frame(ifrVisualizacao)
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, 'divArvoreConteudo')))
                    if self.clicar_botao('Gerar Circular'):
                        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                        self.driver.switch_to.frame(ifrVisualizacao)
                    else:
                        raise(Exception('Não conseguiu clicar no botão Gerar Circular'))
                if len(destinatarios) >= 1:
                    self.driver.execute_script('objLupaDestinatarios.selecionar(700,500);')
                    self.driver.switch_to.default_content()
                    documento_iframe = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, self.config.get(self.sei, 'documento_iframe'))))
                    self.driver.switch_to.frame(documento_iframe)
                    for destinatario in destinatarios:
                        campo = self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_destinatario'))
                        campo.clear()
                        campo.send_keys(destinatario)
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_pesquisar')).click()
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_tabela_destinatario')).click()
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_transpor')).click()
                    self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_fechar')).click()
                    self.driver.switch_to.default_content()
                    ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                    self.driver.switch_to.frame(ifrVisualizacao)
                    if len(destinatarios) == 1:
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_publico')).click()
                        window_before = self.driver.window_handles[0]
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_salvar')).click()
                        self.driver.switch_to.window(window_before)
                    else:
                        self.driver.find_element(By.ID, self.config.get(self.sei, 'documento_gerar_circular')).click()

    def get_anexo(self, anexo, tipo='zip') -> pd.DataFrame:
        if anexo:
            self.go_to(anexo)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        download = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="divArvoreInformacao"]/a')))
        if tipo == 'zip':
            download.click()
        self.driver.switch_to.default_content()

    def is_sobrestado(self, area: str = None, processo: str = None) -> tuple[bool, str]:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'documento_informacao'))))
        sobrestado = 'sobrestado' in informacao.text
        mensagem = informacao.text
        if area:
            regex = '(?im)^(.*)(' + area + ')[^0-9a-z](.*)$'
            matches = search(regex, informacao.text)
            self.driver.switch_to.default_content()
            return sobrestado, matches != None
        else:
            self.driver.switch_to.default_content()
            return sobrestado, mensagem

    def sobrestar_processo(self, motivo, processo: str = None) -> bool:
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        sobrestado, mensagem = self.is_sobrestado(processo)
        if sobrestado:
            return sobrestado
        if self.clicar_botao('Sobrestar Processo'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)
            self.driver.find_element(By.ID, self.config.get(self.sei, 'somente_sobrestar_botao')).click()
            motivoField = self.driver.find_element(By.ID, self.config.get(self.sei, 'motivo_sobrestar_textfield'))
            motivoField.clear()
            motivoField.send_keys(motivo)
            self.driver.find_element(By.ID, self.config.get(self.sei, 'salvar_sobrestamento_botao')).click()
            self.driver.switch_to.default_content()
            return True
        return False

    def remover_sobrestamento(self, processo: str = None) -> bool:
        if processo:
            self.go_to(processo)
        sobrestado, mensagem = self.is_sobrestado(processo)
        if not sobrestado:
            return not sobrestado
        if self.clicar_botao('Remover Sobrestamento do Processo'):
            self.fechar_alerta()
            return True
        return False

    def publicar(self, resumo_ementa: str, data_disponibilizacao: str, documento: str = None, dou: str = False, secao: str = None, pagina:str = None) -> bool:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Agendar Publicação'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
            self.driver.switch_to.frame(ifrVisualizacao)

            resumo_ementa_text_field = self.driver.find_element(By.ID, self.config.get(self.sei, 'resumo_ementa_textfield'))
            resumo_ementa_text_field.clear()
            resumo_ementa_text_field.send_keys(resumo_ementa)

            disponibilizacao = self.driver.find_element(By.ID, self.config.get(self.sei, 'data_disponibilizacao_textfield'))
            disponibilizacao.clear()
            disponibilizacao.send_keys(data_disponibilizacao)

            if dou:
                select = Select(self.driver.find_element(By.ID, self.config.get(self.sei, 'veiculo_textfield')))
                select.select_by_visible_text('DOU')

                select = Select(
                    WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'secao_textfield')))))
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "option[value='" + secao if secao else '3' + "']")))
                select.select_by_visible_text(secao if secao else '3')

                pagina_text_field = self.driver.find_element(By.ID, self.config.get(self.sei, 'pagina_textfield'))
                pagina_text_field.clear()
                pagina_text_field.send_keys(pagina if pagina else '')

                disponibilizacao = self.driver.find_element(By.ID, self.config.get(self.sei, 'data_textfield'))
                disponibilizacao.clear()
                disponibilizacao.send_keys(data_disponibilizacao)

            self.driver.find_element(By.ID, self.config.get(self.sei, 'salvar_button')).click()

            self.driver.switch_to.default_content()
            return True
        return False

    def get_conteudo_documento(self, documento: str = None, tipo: str = 'html'):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        if tipo == 'html':
            try:
                ifrConteudoVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'conteudo_visualizacao'))))
                self.driver.switch_to.frame(ifrConteudoVisualizacao)
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                #ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                #    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
                #self.driver.switch_to.frame(ifrArvoreHtml)
                documento_conteudo = self.driver.find_element(By.XPATH, '/html/body').get_attribute('innerHTML')
                documento_conteudo = sub(r'\\n', '', documento_conteudo)  # retirar quebra de páginas
                documento_conteudo = sub(r'\s\s+?', ' ', documento_conteudo)  # tira espaços duplos
                documento_conteudo = sub(r'&nbsp;', ' ', documento_conteudo)  # tira espaços duplos
                documento_conteudo = documento_conteudo.strip()  # retirar quebras de páginas que tenham restado
                return documento_conteudo
            except:
                raise Exception(f'Conteúdo do documento {documento} não encontrado.')
            finally:
                self.driver.switch_to.default_content()
        elif tipo == 'nato-digital':
            try:
                self.clicar_botao(botao='Consultar/Alterar Documento Externo')
                ifrConteudoVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'conteudo_visualizacao'))))
                self.driver.switch_to.frame(ifrConteudoVisualizacao)
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                tabela_anexos = self.driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/form[2]/div[2]/table/tbody/tr')
                arquivos = []
                for row in tabela_anexos:
                    nome_arquivo = (
                        row.find_element(By.XPATH, "td[2]")
                        .text
                        .strip()
                    )
                    row.find_element(By.XPATH, 'td[8]/div/a').click()
                    #arquivo = os.path.join(self.diretorio,nome_arquivo)
                    arquivo = f'{self.diretorio}\\{nome_arquivo}'
                    contador = 0
                    import time
                    while not os.path.isfile(arquivo) and contador <= 3:
                        time.sleep(1)
                        contador += 1
                    arquivos.append(arquivo)
                return arquivos
            except:
                raise Exception(f'Conteúdo do documento {documento} não encontrado.')
            finally:
                self.driver.switch_to.default_content()

    def get_documento_element_by_id(self, id: str, documento: str = None) -> str:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
                self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.find_element(By.ID, id).text
        except:
            raise Exception(f'Conteúdo do documento {documento} não encontrado.')
        finally:
            self.driver.switch_to.default_content()

    def get_documento_elements_by_id(self, id: str, documento: str = None) -> list:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
                self.driver.switch_to.frame(ifrArvoreHtml)
            elements = self.driver.find_elements_by_id(id)
            return [element.text for element in elements]
        except:
            raise Exception(f'Conteúdo do documento {documento} não encontrado.')
        finally:
            self.driver.switch_to.default_content()

    def get_documento_element_by_xpath(self, xpath: str, documento: str = None) -> str:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if(self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
                self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.find_element_by_xpath(xpath).text
        except:
            raise Exception(f'Conteúdo do documento {documento} não encontrado.')
        finally:
            self.driver.switch_to.default_content()

    def get_documento_elements_by_xpath(self, xpath: str, documento: str = None) -> list:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
                self.driver.switch_to.frame(ifrArvoreHtml)
            elements = self.driver.find_elements_by_xpath(xpath)
            return [element.text for element in elements]
        except:
            raise Exception(f'Conteúdo do documento {documento} não encontrado.')
        finally:
            self.driver.switch_to.default_content()

    def listar_documentos(self, processo: str = None) -> list:
        raise Exception('Método não implementado')
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        ifrArvore = WebDriverWait(self.driver, 3).until(#//*[@id="div6807594"]
            EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'arvore_frame'))))
        self.driver.switch_to.frame(ifrArvore)

        lista_documentos = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'lista_documentos'))))
        arvore = lista_documentos.find_element(By.XPATH, 'div/div')
        elements = arvore.find_elements(By.XPATH, './/*')

        documentos = {
            'NOME': [],
            'NUMERO': [],
            'ÁREA': [],
            'ASSINADO': [],
        }
        if len(elements) > 0:
            for i, element in enumerate(elements):
                if i <= 2:
                    continue
                if i == 3:
                    nome_numero = element.text
                    print(element.text)
                    nome_numero = nome_numero.split('(')
                    nome_numero = [n.strip() for n in nome_numero]
                    nome_numero[-1] = nome_numero[-1].replace(')', '')
                    documentos['NOME'].append(nome_numero[0])
                    documentos['NUMERO'].append(nome_numero[1])
                    continue
                tag_name = element.type_name
                if tag_name != 'span':
                    continue
                if tag_name == 'img':
                    continue
                nome_numero = element.text
                nome_numero = nome_numero.split('(')
                nome_numero = [n.strip() for n in nome_numero]
                nome_numero[-1] = nome_numero[-1].replace(')', '')
                documentos['NOME'].append(nome_numero[0])
                documentos['NUMERO'].append(nome_numero[1])
        self.driver.switch_to.default_content()
        return documentos

    def incluir_em_bloco(self, bloco:str = None, documento:str = None) -> bool:
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        self.clicar_botao('Incluir em Bloco')
        conteudo_visualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'conteudo_visualizacao'))))
        self.driver.switch_to.frame(conteudo_visualizacao)
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, self.config.get(self.sei, 'visualizacao_frame'))))
        self.driver.switch_to.frame(ifrVisualizacao)
        blocos = Select(self.driver.find_element(By.ID, self.config.get(self.sei, 'lista_blocos')))
        blocos.select_by_value(bloco)
        self.driver.find_element(By.ID, self.config.get(self.sei, 'incluir_em_bloco')).click()
        self.fechar_alerta()
        self.driver.switch_to.default_content()
        return True
            
    def close(self, voltar: bool = True):
        if voltar and self.__area_inicial:
            self.seleciona_area(self.__area_inicial)
        self.driver.close()
        self.driver.quit()