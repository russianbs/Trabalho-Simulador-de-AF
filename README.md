# Trabalho Simulador de Autômatos Finitos
:warning: Este trabalho está incompleto, já que simula AFNDs e AFDs mas não simula AFND com movimento vazio.

## Introdução
Esta ferramenta foi escrita utilizando a linguagem Python, como requerido ela funciona por chamada de linha de comando e seu uso dessa forma será explicado mais à frente.

A ferramente funciona lendo um arquivo Json contendo as especificações e regras do autômato, como também lendo um arquivo CSV com as palavaras que serão processadas, assim determinando qual tipo de autõmato deve ser utilizado para o processamento e realizando o processamento, escrevendo os resultados no padrão requerido em um arquivo de output CSV.

## Overview geral do código
```python
class Transicao:
    def __init__(self, de, para, simbolo):
        self.de = int(de)
        self.para = int(para)
        self.simbolo = simbolo
        
class Automato:
    def __init__(self, estadoInicial, estadosFinais, transicoes):
        self.estadoInicial = estadoInicial
        self.estadosFinais = estadosFinais
        self.transicoes = transicoes
```
A primeira classe cria um modelo para representar as mudanças de estado de um automato, cada transição diz de qual estado a máquina sai, para qual estado ela vai, e qual símbolo faz isso acontecer.
A segunda classe define o autômato em si, em qual estado ele começa, quais estados são considerados finais, e todas as suas transições.

```python
def lerAutomato(arquivo_json):
    with open(arquivo_json, "r") as f:
        dados = json.load(f)
        transicoes = []
        for t in dados["transitions"]:
            transicoes.append(Transicao(t["from"], t["to"], t["read"]))
        return Automato(
            dados["initial"],
            dados["final"],
            transicoes
        )
```
Esta função lê o arquivo Json que foi recebido de argumento na função main através de linha de comando, a função lê o arquivo e as características do autõmato, retornando um objeto à classe Automato contendo estas características.

```python
def determinarAutomato(automato):
    pares = {}
    for t in automato.transicoes:
        chave = (t.de, t.simbolo)
        if chave in pares:
            return "AFND"
        pares[chave] = t.para
    return "AFD"
```
Esta função verifica se o autômato é determinístico (AFD) ou não determinístico (AFND), para isso, ela analisa as transições, existir mais de uma transição com o mesmo símbolo a partir do mesmo estado, o autômato é considerado AFND, caso contrário, ele é AFD.

```python
def simularAFD(automato, palavra):
    estadoAtual = automato.estadoInicial
    for simbolo in palavra:
        transicoes = [t for t in automato.transicoes if t.de == estadoAtual and t.simbolo == simbolo]
        if not transicoes:
            return False
        estadoAtual = transicoes[0].para
    return estadoAtual in automato.estadosFinais
```
Esta função é responsável por simular o comportamento de um AFD, processando palavras de entrada, percorrendo cada símbolo dela buscando uma transição que corresponda ao símbolo atual e ao estado em que o autômato se encontra. Se não encontrar uma transição válida, a função encerra imediatamente e retorna False, indicando que a palavra foi rejeitada. Caso contrário, atualiza o estado atual com base na transição encontrada e continua a simulação. Ao final da palavra, verifica se o estado em que o autômato terminou está entre os estados finais definidos; se estiver, a palavra é aceita (True), caso contrário, rejeitada (False), utilizando compreensão de listas para filtrar as transições.

```python
def simularAFND(automato, palavra):
    estados_atuais = set([automato.estadoInicial])
    for simbolo in palavra:
        proximos = set()
        for estado in estados_atuais:
            for t in automato.transicoes:
                if t.de == estado and t.simbolo == simbolo:
                    proximos.add(t.para)
        if not proximos:
            return False
        estados_atuais = proximos
    return any(e in automato.estadosFinais for e in estados_atuais)
```
Esta função simula o funcionamento de um autômato finito não determinístico, a cada símbolo da palavra, ela verifica todas as transições possíveis a partir dos estados atuais e guarda os estados alcançáveis. Se em algum momento não houver transições para continuar a palavra é rejeitada, fim da leitura, se algum dos estados ativos for final, a palavra é considerada aceita.

```python
def main():
    if len(sys.argv) != 4:
        print("Uso: ferramenta arquivo_do_automato.aut arquivo_de_testes.in arquivo_de_saida.out")
        return

    arquivo_automato = sys.argv[1]
    arquivo_testes = sys.argv[2]
    arquivo_saida = sys.argv[3]

    automato = lerAutomato(arquivo_automato)
    tipo = determinarAutomato(automato)

    with open(arquivo_testes, "r") as f:
        leitor = csv.reader(f, delimiter=";")
        with open(arquivo_saida, "w") as saida:
            for linha in leitor:
                palavra = linha[0]
                esperado = linha[1] == "1"

                inicio = time.perf_counter()
                if tipo == "AFD":
                    resultado = simularAFD(automato, palavra)
                else:
                    resultado = simularAFND(automato, palavra)
                fim = time.perf_counter()

                tempo_ms = (fim - inicio) * 1000
                saida.write(f"{palavra};{1 if esperado else 0};{1 if resultado else 0};{tempo_ms:.3f}\n")

if __name__ == "__main__":
    main()
```
A função main começa verificando se o número correto de argumentos foi passado via linha de comando (3 argumentos: o arquivo do autômato, o arquivo de testes e o arquivo de saída), se estes argumentos não inseridos de forma correta, ela encerra o processo. Depois, ela faz com que a função de leitura leia o arquivo Json contendo o autõmato, após isso determina se o autõmato é AFND ou AFD utilizando a função "determinarAutomato", então simulando o autômato com a função correspondente ao seu tipo enquanto calcula o tempo desse processamento em milisegundos, por fim escrevendo os resultados no arquivo de saída .out.

## Resumo de funcionamento
O programa é chamado por linha de comando com os argumentos dos arquivos que serão recebidos na Main, após isso o programa lê o arquivo Json com as especificações do autômato e a armazena na classe "Automato", após isso o tipo é determinado pela função "determinarAutomato" que verifica se existem mais de uma transição com o mesmo símbolo saindo de um estado para outros, com o tipo definido a função Main abre o arqivuo de saída .out/CSV e entra em um loop for, aqui ela toma o tempo do sistema no começo da execução da função de simulação correspondente, "simularAFND" ou "simularAFD", após a simulação ser concluída ela toma o tempo do sistema novamente e acha o tempo de processamento de cada palavra subtraindo o tempo inicial do final, ainda dentro do loop for ela printa os resultados do processamento de cada palavra conforme o padrão pedido dentro do arquivo .out.

## Como utilizar
Para utilizar a ferramenta, abra o Shell e mude o diretório atual para o diretório onde o arquivo ferramenta.py está, após isso o programa e seus argumentos devem ser chamados por linha de comando da seguinte maneira:
```python simulador.py automato.aut entrada.in saida.out ```


