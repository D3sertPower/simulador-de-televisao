import numpy as np
import heapq
QUANTIDADE_DE_CANAIS = 25
QUANTIDADE_DE_PROGRAMAS = 100
NUMERO_DE_TELESPECTADORES = 1000
MINUTOS_EM_UM_DIA = 1440
DIAS_DE_SIMULACAO = 100 # quantos dias você vai simular
canais = []
programas = []
telespectadores = []
minutagens = [15,30,45,60] # opções de duração para um programa
with open('br-sem-acentos.txt', 'r') as palavras:
    lista_de_palavras = palavras.read().split()

complementos_inicio = ['','O','A']
opcoes_de_palavra = []
generos = ['Esportes','Novelas','Informação','Conversas','Game Shows','Reality Shows']
for p in range(0, len(lista_de_palavras)):
    if len(lista_de_palavras[p]) <= 10 and lista_de_palavras[p] not in complementos_inicio and lista_de_palavras[p]:
        opcoes_de_palavra.append(lista_de_palavras[p].capitalize())

class Programa:
    def __init__(self, id_canal_dono: int, nome: str, id: int, duracao: int, status_popular: bool, genero: str):
        self.id_canal_dono = id_canal_dono
        self.nome = nome
        self.id = id
        self.status_popular = status_popular
        self.duracao = duracao # horário, em minutos, de duração do programa
        self.genero = genero

    def atualizar_popularidade(self, status_popular: bool):
        self.status_popular = status_popular

Intervalo_Comercial = Programa(None,'Intervalo Comercial',-1,5,False,'Informação')
# para o intervalo comercial, é o programa de ID -1 de nenhum canal, com nenhum horário específico e impopular.
Jornal = Programa(None,'Jornal',0,10,False,'Informação')
# para o jornal temos a mesma situação só que com o ID 0.


class Canal:
    def __init__(self, id: int, nome: str):
        self.nome = nome
        self.id = id
        self.programacao = [Intervalo_Comercial, Jornal]
        self.horario_inicio_programa = None
        self.indice_programa_atual = 0 # Guarda o índice atual para otimizar a virada de programa
        self.espectadores = 0

    def atualizar_programacao(self, programa): # remove ou adiciona um programa a um canal
        if programa not in self.programacao:
            self.programacao.append(programa)
        else:
            self.programacao.remove(programa)

    def troca_programa(self, indice): # troca o programa que está passando no canal
        if self.espectadores > 3*NUMERO_DE_TELESPECTADORES/QUANTIDADE_DE_CANAIS: # checamos antes de trocar o programa se o canal está bombando.
            self.programacao[self.indice_programa_atual].atualizar_popularidade(True)
        else:
            self.programacao[self.indice_programa_atual].atualizar_popularidade(False)
        if 0 <= indice < len(self.programacao):
            self.indice_programa_atual = indice
        else: print('Erro na função troca_programa')

    def atualizar_espectadores(self, estado: bool): # estado, se True, é para adicionar um espectador, se False, é para remover um espectador
        if estado == False:
            self.espectadores -= 1
        else:
            self.espectadores += 1

    # cria os canais e programas adequadamente:
for i in range(1, QUANTIDADE_DE_CANAIS+1):
    nome_de_canal = np.random.choice(opcoes_de_palavra)
    canais.append(Canal(i, nome_de_canal))
for k in range(1, QUANTIDADE_DE_PROGRAMAS+1):
    complemento_inicial = np.random.choice(complementos_inicio)
    genero = np.random.choice(generos)
    if complemento_inicial != '':
        nome_de_programa = complemento_inicial + '__' + np.random.choice(opcoes_de_palavra)
    else:
        nome_de_programa = np.random.choice(opcoes_de_palavra)
    duracao = np.random.choice(minutagens)
    id_dono_do_canal = np.random.randint(1, QUANTIDADE_DE_CANAIS)
    novo_programa = Programa(id_dono_do_canal, nome_de_programa, k, duracao, False, genero)
    programas.append(novo_programa)
    if len(canais[id_dono_do_canal-1].programacao) < int(QUANTIDADE_DE_PROGRAMAS/5): # Não queremos canais com programas demais.
        canais[id_dono_do_canal-1].atualizar_programacao(novo_programa) # Adicionamos o programa a programação de algum canal
    else:
        id_dono_do_canal = np.random.randint(1, QUANTIDADE_DE_CANAIS)
        novo_programa.id_canal_dono = id_dono_do_canal
        canais[id_dono_do_canal-1].atualizar_programacao(novo_programa) # De fato, permitimos canais com apenas o Jornal e Intervalos Comerciais.
    if np.random.randint(1,101) <= 10:
        canais[id_dono_do_canal-1].atualizar_programacao(Intervalo_Comercial)
    if np.random.randint(1,101) <= 5:
        canais[id_dono_do_canal-1].atualizar_programacao(Jornal)
# Configuração dos Telespectadores

# Pesos de preferência de gênero por faixa etária: [Esportes, Novelas, Informação, Conversas, Game Shows, Reality Shows]
# Cada linha é uma faixa: 0=Criança, 1=Jovem, 2=Adulto, 3=Idoso
PESOS_GENERO_POR_FAIXA = np.array([
    [0.05, 0.10, 0.05, 0.10, 0.40, 0.30], # Criança: prefere Game Shows e Reality Shows
    [0.25, 0.10, 0.10, 0.15, 0.20, 0.20], # Jovem: prefere Esportes, Game Shows e Reality Shows
    [0.20, 0.20, 0.25, 0.20, 0.10, 0.05], # Adulto: prefere Informação e Esportes
    [0.10, 0.25, 0.30, 0.25, 0.05, 0.05], # Idoso: prefere Novelas, Informação e Conversas
])

# Probabilidade de cada faixa etária ser gerada na população
DISTRIBUICAO_FAIXAS = [0.15, 0.25, 0.40, 0.20]

# Quanto maior a faixa etária, maior a fixação por programas populares
FIXACAO_POPULAR_POR_FAIXA = np.array([0.05, 0.15, 0.30, 0.50])

class Telespectador:
    def __init__(self, id: int, faixa_etaria: int, pesos_genero: np.ndarray, paciencia: int):
        self.id = id
        self.faixa_etaria = faixa_etaria # 0 -> Criança, 1 -> Jovem, 2 -> Adulto, 3 -> Idoso
        self.pesos_genero = pesos_genero # pesos de preferência para cada gênero, somam 1.0
        self.paciencia = paciencia # quantidade de canais que passa antes de desistir e parar em algum
        self.fixacao_popular = FIXACAO_POPULAR_POR_FAIXA[faixa_etaria] # chance de parar em programa popular independente do gênero
        self.canal_atual = np.random.randint(1, QUANTIDADE_DE_CANAIS + 1) # canal onde está agora
        self.canais_favoritos = [] # canais onde já encontrou programas do seu agrado
        self.genero_favorito = generos[np.argmax(pesos_genero)] # gênero com maior peso
        self.canais_zarpados = 0 # total acumulado de canais que já passou
        self.em_busca = True # se está passando canais ou assistindo satisfeito

    def _trocar_canal(self, novo_id_canal):
        # Atualiza os contadores de espectadores e o dicionário de lookup ao mudar de canal
        canais[self.canal_atual - 1].atualizar_espectadores(False)
        telespectadores_por_canal[self.canal_atual].discard(self.id)
        self.canal_atual = novo_id_canal
        canais[self.canal_atual - 1].atualizar_espectadores(True)
        telespectadores_por_canal[self.canal_atual].add(self.id)
        self.canais_zarpados += 1

    def avaliar_programa(self, programa):
        # Telespectador avalia o programa atual e decide se fica ou continua procurando
        if programa.genero is None or programa.id_canal_dono is None:
            # Programas especiais (intervalo comercial, jornal) sempre ativam a busca
            self.em_busca = True
            return
        peso_do_genero = self.pesos_genero[generos.index(programa.genero)]
        gosta_do_genero = np.random.random() < peso_do_genero
        gosta_por_popularidade = programa.status_popular and np.random.random() < self.fixacao_popular
        if gosta_do_genero or gosta_por_popularidade:
            # Gostou do programa: para de buscar e registra o canal como favorito
            self.em_busca = False
            if programa.id_canal_dono not in self.canais_favoritos:
                self.canais_favoritos.append(programa.id_canal_dono)
        else:
            self.em_busca = True

    def buscar_canal(self):
        # Tenta ir para um canal favorito primeiro; se não estiver passando algo do agrado, zarpa
        if self.canais_favoritos:
            canal_favorito = canais[np.random.choice(self.canais_favoritos) - 1]
            programa_no_favorito = canal_favorito.programacao[canal_favorito.indice_programa_atual]
            peso_do_genero = self.pesos_genero[generos.index(programa_no_favorito.genero)] if programa_no_favorito.genero else 0
            if np.random.random() < peso_do_genero:
                # O canal favorito está passando algo do agrado: vai direto
                self._trocar_canal(canal_favorito.id)
                self.avaliar_programa(programa_no_favorito)
                return
        # Sem canal favorito adequado: zarpa até esgotar a paciência
        for _ in range(self.paciencia):
            novo_canal = np.random.randint(1, QUANTIDADE_DE_CANAIS + 1)
            self._trocar_canal(novo_canal)
            programa_no_canal = canais[self.canal_atual - 1].programacao[canais[self.canal_atual - 1].indice_programa_atual]
            self.avaliar_programa(programa_no_canal)
            if not self.em_busca:
                return
        # Esgotou a paciência: fica onde está mesmo sem gostar

# Geração vetorizada dos telespectadores com numpy
faixas = np.random.choice([0,1,2,3], size=NUMERO_DE_TELESPECTADORES, p=DISTRIBUICAO_FAIXAS)
paciencias = np.random.randint(2, 11, size=NUMERO_DE_TELESPECTADORES) # paciência entre 2 e 10 canais

for t in range(NUMERO_DE_TELESPECTADORES):
    faixa = faixas[t]
    pesos = PESOS_GENERO_POR_FAIXA[faixa].copy()
    # Adiciona variação individual nos pesos para que telespectadores da mesma faixa não sejam idênticos
    variacao = np.random.dirichlet(pesos * 10) # dirichlet preserva a soma=1 e respeita a direção dos pesos originais
    telespectador = Telespectador(t, faixa, variacao, int(paciencias[t]))
    telespectadores.append(telespectador)

# Dicionário que mapeia id_canal -> conjunto de ids de telespectadores assistindo agora
telespectadores_por_canal = {canal.id: set() for canal in canais}

# Avaliação inicial: cada telespectador registra sua presença no canal inicial e avalia o programa
for t in telespectadores:
    canais[t.canal_atual - 1].atualizar_espectadores(True) # registra presença sem contar como zap
    telespectadores_por_canal[t.canal_atual].add(t.id)
    canal_inicial = canais[t.canal_atual - 1]
    programa_inicial = canal_inicial.programacao[canal_inicial.indice_programa_atual]
    t.avaliar_programa(programa_inicial)
    if t.em_busca:
        t.buscar_canal()

# Inicialização dos canais e suas programações
fila_de_eventos = []
for canal in canais:
    indice_inicial = len(canal.programacao) - 1 if len(canal.programacao) > 2 else 1
    canal.indice_programa_atual = indice_inicial
    canal.horario_inicio_programa = 0
    programa_inicial = canal.programacao[indice_inicial]
    heapq.heappush(fila_de_eventos, (programa_inicial.duracao, canal.id))

# Aqui iniciamos os eventos que dependem do relógio da simulação.
DURACAO_SIMULACAO = MINUTOS_EM_UM_DIA * DIAS_DE_SIMULACAO

while fila_de_eventos:
    relogio, id_canal = heapq.heappop(fila_de_eventos)
    if relogio > DURACAO_SIMULACAO:
        break
    canal = canais[id_canal - 1]
    proximo_indice = (canal.indice_programa_atual + 1) % len(canal.programacao)
    canal.troca_programa(proximo_indice)
    canal.horario_inicio_programa = relogio
    proximo_programa = canal.programacao[canal.indice_programa_atual]
    heapq.heappush(fila_de_eventos, (relogio + proximo_programa.duracao, id_canal))
    # Notifica apenas os telespectadores que estão neste canal para reagirem à troca de programa
    for id_t in list(telespectadores_por_canal[id_canal]):
        t = telespectadores[id_t]
        t.avaliar_programa(proximo_programa)
        if t.em_busca:
            t.buscar_canal()