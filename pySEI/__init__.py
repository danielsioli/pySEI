from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from re import match

class Sei:

    def __init__(self, headless=True,executable_path='chromedriver'):
        chrome_options = Options()
        chrome_options.add_argument('--headless ' if headless else '' + '--enable-javascript')
        self.driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)

    def start_driver(self, url, usuario, senha):
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

    def go_to(self, numero_sei):
        self.driver.switch_to.default_content()
        pesquisa = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "txtPesquisaRapida")))
        pesquisa.clear()
        pesquisa.send_keys(str(numero_sei))
        formPesquisaRapida = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.ID, "frmProtocoloPesquisaRapida")))
        formPesquisaRapida.submit()

    def is_processo_aberto(self, processo, area):
        self.go_to(processo)
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divInformacao")))
        regex = '(?im)^(.*)(' + area + ')[^0-9a-z](.*)$'
        matches = match(regex, informacao.text)
        aberto = False
        if matches:
            aberto = True
        self.driver.switch_to.default_content()
        return aberto

    def get_processo_anexador(self, processo):
        self.go_to(processo)
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
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        arvore = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divArvoreAcoes")))
        botoes = arvore.find_elements(By.XPATH, '//*[@id=\"divArvoreAcoes\"]/a')

        for b in botoes:
            img = b.find_element(By.XPATH, 'img')
            if botao in img.get_attribute('title'):
                b.click()
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

    def is_sobrestado(self, processo, area=None):
        self.go_to(processo)
        ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
        self.driver.switch_to.frame(ifrVisualizacao)
        informacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divInformacao")))
        sobrestado = 'sobrestado' in informacao.text
        mensagem = informacao.text
        regex = '(?im)^(.*)(' + area + ')[^0-9a-z](.*)$'
        matches = match(regex,informacao.text)
        self.driver.switch_to.default_content()
        if area:
            return sobrestado, matches != None
        else:
            return sobrestado, mensagem

    def sobrestar_processo(self, processo, motivo):
        self.go_to(processo)
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

    def remover_sobrestamento(self, processo):
        self.go_to(processo)
        if self.clicar_botao('Remover Sobrestamento do Processo'):
            self.fechar_alerta()
            return True
        return False

    def publicar(self, documento, resumo_ementa, data_disponibilizacao, dou=False, secao=None, pagina=None):
        self.go_to(documento)
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

    def get_conteudo_documento(self, documento):
        self.go_to(documento)

        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            ifrArvoreHtml = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
            self.driver.switch_to.frame(ifrArvoreHtml)
            documento_conteudo = self.driver.find_element_by_xpath('/html/body').get_attribute('innerHTML')
            return documento_conteudo
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_element_by_id(self,documento,id):
        self.go_to(documento)

        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
            self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.driver.find_element_by_id(id)
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def get_documento_element_by_xpath(self,documento,xpath):
        self.go_to(documento)

        try:
            ifrVisualizacao = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "ifrVisualizacao")))
            self.driver.switch_to.frame(ifrVisualizacao)
            ifrArvoreHtml = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))
            self.driver.switch_to.frame(ifrArvoreHtml)
            return self.driver.driver.find_element_by_xpath(xpath)
        except:
            raise Exception('Conteúdo do documento %s não encontrado.' % documento)
        finally:
            self.driver.switch_to.default_content()

    def close(self):
        self.driver.close()
        self.driver.quit()