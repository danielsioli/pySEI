from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from re import search,sub
from getpass import getpass
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import DriverManager as MsDriverManager

class Sei:

    __area_inicial = None
    __windows_before = 0
    __windows_after = 0

    def __init__(self, headless=False, executable_path='chromedriver'):
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
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        elif 'msedgedriver' in executable_path:
            edge_options = EdgeOptions()
            edge_options.use_chromium = True
            edge_options.add_argument('enable-javascript')
            edge_options.add_argument('window-size=1440,900')
            edge_options.add_argument("disable-extensions")
            edge_options.add_argument("proxy-server='direct://'")
            edge_options.add_argument("proxy-bypass-list=*")
            edge_options.add_argument("start-maximized")
            edge_options.add_argument('disable-dev-shm-usage')
            edge_options.add_argument('no-sandbox')
            edge_options.add_argument('ignore-certificate-errors')
            if headless:
                edge_options.add_argument('headless')
                edge_options.add_argument('disable-gpu')
            self.driver = Edge(executable_path=MsDriverManager.install(), options=edge_options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start_driver(self, url, usuario=None, senha=None):

        if usuario == None:
            usuario = input('Digite o usuário: ')
        if senha == None:
            senha = getpass('Digite a senha: ')

        self.driver.get(url)

        usuario_field = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "txtUsuario")))

        senha_field = self.driver.find_element_by_id('pwdSenha')
        botao_acessar = self.driver.find_element_by_id('sbmLogin')

        usuario_field.clear()
        usuario_field.send_keys(usuario)
        senha_field.clear()
        senha_field.send_keys(senha)
        botao_acessar.click()
        alerta = self.fechar_alerta()
        if alerta:
            raise Exception(alerta)  # usuário ou senha inválido
        self.__area_incial = self.get_area()

    def go_to(self, numero_sei):
        if self.__windows_after > self.__windows_before:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[self.__windows_before - 1])
        self.driver.switch_to.default_content()
        pesquisa = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "txtPesquisaRapida")))
        pesquisa.clear()
        pesquisa.send_keys(str(numero_sei))
        formPesquisaRapida = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, "frmProtocoloPesquisaRapida")))
        self.__windows_before = len(self.driver.window_handles)
        formPesquisaRapida.submit()
        self.__windows_after = len(self.driver.window_handles)
        if self.__windows_after > self.__windows_before:
            self.driver.switch_to.window(self.driver.window_handles[self.__windows_after - 1])

    def is_processo_aberto(self, area=None, processo=None):
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            informacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divInformacao")))
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

    def get_processo_anexador(self, processo=None):
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divInformacao")))
        procAnex = None
        if 'Processo anexado ao processo' in informacao.text:
            processoAnexador = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"divInformacao\"]/div/a")))
            procAnex = processoAnexador.text
        self.driver.switch_to.default_content()
        return procAnex

    def get_area(self):
        self.driver.switch_to.default_content()
        select = Select(self.driver.find_element_by_id('selInfraUnidades'))
        return select.all_selected_options[0].text

    def seleciona_area(self, area):
        self.driver.switch_to.default_content()
        select = Select(self.driver.find_element_by_id('selInfraUnidades'))
        all_selected_options = select.all_selected_options
        for option in all_selected_options:
            if area == option.text:
                return True

        select = Select(self.driver.find_element_by_id('selInfraUnidades'))
        options = select.options
        for option in options:
            if area == option.text:
                select.select_by_visible_text(area)
                Select(WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'selInfraUnidades'))))
                return True

        return False

    def clicar_botao(self, botao):
        self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        arvore = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divArvoreAcoes")))
        botoes = arvore.find_elements(By.XPATH, '//*[@id=\"divArvoreAcoes\"]/a')

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

    def fechar_alerta(self):
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

    def is_sobrestado(self, area=None, processo=None):
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divInformacao")))
        sobrestado = 'sobrestado' in informacao.text
        mensagem = informacao.text
        self.driver.switch_to.default_content()
        if area:
            regex = '(?im)^(.*)(' + area + ')[^0-9a-z](.*)$'
            matches = search(regex, informacao.text)
            return sobrestado, matches != None
        else:
            return sobrestado, mensagem

    def sobrestar_processo(self, motivo, processo=None):
        if processo:
            self.go_to(processo)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Sobrestar Processo'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            self.driver.find_element(By.ID, 'divOptSomenteSobrestar').click()
            motivoField = self.driver.find_element(By.ID, 'txaMotivo')
            motivoField.clear()
            motivoField.send_keys(motivo)
            self.driver.find_element(By.ID, 'sbmSalvar').click()
            self.driver.switch_to.default_content()
            return True
        return False

    def remover_sobrestamento(self, processo=None):
        if processo:
            self.go_to(processo)
        if self.clicar_botao('Remover Sobrestamento do Processo'):
            self.fechar_alerta()
            return True
        return False

    def publicar(self, resumo_ementa, data_disponibilizacao, documento=None, dou=False, secao=None, pagina=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        if self.clicar_botao('Agendar Publicação'):
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)

            resumo_ementa_text_field = self.driver.find_element(By.ID, 'txaResumo')
            resumo_ementa_text_field.clear()
            resumo_ementa_text_field.send_keys(resumo_ementa)

            disponibilizacao = self.driver.find_element(By.ID, 'txtDisponibilizacao')
            disponibilizacao.clear()
            disponibilizacao.send_keys(data_disponibilizacao)

            if dou:
                select = Select(self.driver.find_element_by_id('selVeiculoIO'))
                select.select_by_visible_text('DOU')

                select = Select(WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "selSecaoIO"))))
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='" + secao if secao else '3' + "']")))
                select.select_by_visible_text(secao if secao else '3')

                pagina_text_field = self.driver.find_element(By.ID, 'txtPaginaIO')
                pagina_text_field.clear()
                pagina_text_field.send_keys(pagina if pagina else '')

                disponibilizacao = self.driver.find_element(By.ID, 'txtDataIO')
                disponibilizacao.clear()
                disponibilizacao.send_keys(data_disponibilizacao)

            self.driver.find_element_by_id('btnSalvar').click()

            self.driver.switch_to.default_content()
            return True
        return False

    def get_conteudo_documento(self, documento=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            ifrArvoreHtml = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
            self.driver.switch_to.frame(ifrArvoreHtml)
            documento_conteudo = self.driver.find_element_by_xpath('/html/body').get_attribute('innerHTML')
            documento_conteudo = sub(r'\\n', '', documento_conteudo)  # retirar quebra de páginas
            documento_conteudo = sub(r'\s\s+?', ' ', documento_conteudo)  # tira espaços duplos
            documento_conteudo = sub(r'&nbsp;', ' ', documento_conteudo)  # tira espaços duplos
            documento_conteudo = documento_conteudo.strip()  # retirar quebras de páginas que tenham restado
            return documento_conteudo
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_element_by_id(self,id, documento=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
                self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.find_element_by_id(id).text
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_elements_by_id(self,id, documento=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
                self.driver.switch_to.frame(ifrArvoreHtml)
            elements = self.driver.find_elements_by_id(id)
            return [element.text for element in elements]
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_element_by_xpath(self,xpath,documento=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if(self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
                self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.find_element_by_xpath(xpath).text
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_elements_by_xpath(self,xpath,documento=None):
        if documento:
            self.go_to(documento)
        else:
            self.driver.switch_to.default_content()
        try:
            if (self.__windows_after == self.__windows_before):
                ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
                self.driver.switch_to.frame(ifrVisualizacao)
                ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
                self.driver.switch_to.frame(ifrArvoreHtml)
            elements = self.driver.find_elements_by_xpath(xpath)
            return [element.text for element in elements]
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def close(self,voltar=True):
        if voltar:
            self.seleciona_area(self.__area_incial)
        self.driver.close()
        self.driver.quit()