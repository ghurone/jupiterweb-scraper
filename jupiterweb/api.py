import requests
from bs4 import BeautifulSoup


def buscar_disciplina_por_codigo(codigo:str) -> dict:
    URL = 'https://uspdigital.usp.br/jupiterweb/obterDisciplina'
    
    req = requests.get(URL, params={'sgldis': codigo})
    
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'lxml')
        
        msg = soup.find('div', attrs={'id':'web_mensagem'})
        if msg:
            raise ValueError(msg.text.strip())
        
        tabela_bruta = soup.find('form', attrs={'name':'form1'}).find_all('span')
        itens = ['Instituto', 'Departamento', 'Nome disciplina', 'Nome inglês']
        conteudo = {}
        
        i = 0
        for row in tabela_bruta:
            cls = row.attrs.get('class')[0]
            
            if cls == 'txt_arial_8pt_black':
                chave = row.text.strip().replace(':', '')
                conteudo[chave] = ''
                
                if chave == 'Docente(s) Responsável(eis)':
                    conteudo[chave] = []
                
            elif cls == 'txt_arial_8pt_gray':
                texto = row.text.strip().replace('\n','').replace('\t', '').replace('\r', '').replace('\xa0', ' ')
                
                if texto:
                    if chave == 'Docente(s) Responsável(eis)':
                        conteudo[chave].append(texto)
                    else:
                        conteudo[chave] += texto
                        
            elif cls == 'txt_arial_10pt_black':
                conteudo[itens[i]] = row.text.strip() 
                i += 1
                
        return Disciplina(conteudo)
            
    else:
        raise requests.HTTPError(f'erro: {req.status_code}')
    
    
def buscar_disciplina_por_nome(nome:str):
    nome = nome.strip()
    
    if len(nome) > 30:
        raise ValueError('A sua busca é muito grande')
    
    URL = 'https://uspdigital.usp.br/jupiterweb/obterDisciplina'
    
    req = requests.get(URL, params={'nomdis':nome})
    
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'lxml')
        
        msg = soup.find('div', attrs={'id':'web_mensagem'})
        if msg:
            raise ValueError(msg.text.strip())
        
        tabela_bruta = soup.find(lambda tag:tag.name == "table" and len(tag.attrs) == 2).find_all('a')
        disc = []
        
        for row in tabela_bruta:
            disc.append((row.attrs['href'][23:30], row.text))
            
        return Disciplinas(disc)
        
    else:
        raise requests.HTTPError(f'erro: {req.status_code}')
    
    
class Disciplina:
    def __init__(self, dicio:dict) -> None:
        self.sigla, self.nome = dicio['Nome disciplina'][12:19], dicio['Nome disciplina'][22:]
        self.departamento = dicio['Departamento']
        self.instituto = dicio['Instituto']
        self.nome_en = dicio['Nome inglês']
        
        self.cred_aula = dicio['Créditos Aula']
        self.cred_trab = dicio['Créditos Trabalho']
        self.carga_horaria = dicio['Carga Horária Total']
        self.tipo = dicio['Tipo']
        self.data_ativação = dicio['Ativação']
        self.data_desativação = dicio['Desativação']
        
        try:
            self.docentes = dicio['Docente(s) Responsável(eis)']
        except KeyError:
            self.docentes = []
        
        self.objetivos = dicio['Objetivos']
        self.programa_resumido = dicio['Programa Resumido']
        self.programa = dicio['Programa']
        self.avaliação = {'Método': dicio['Método'], 'Critério': dicio['Critério'],
                          'Norma de Recuperação': dicio['Norma de Recuperação']}
        self.bibliografia = dicio['Bibliografia']


class Disciplinas:
    def __init__(self, lista:list) -> None:
        self.lista = lista
    
    def __str__(self) -> str:
        return str(self.lista)
    
    def __repr__(self) -> str:
        return repr(self.lista)
    
    def __getitem__(self, item):
        return buscar_disciplina_por_codigo(self.lista[item][0])