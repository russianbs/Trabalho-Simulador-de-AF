import sys
import json
import csv
import time  


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
        
def determinarAutomato(automato):
    pares = {}
    for t in automato.transicoes:
        chave = (t.de, t.simbolo)
        if chave in pares:
            return "AFND"
        pares[chave] = t.para
    return "AFD"

def simularAFD(automato, palavra):
    estadoAtual = automato.estadoInicial
    for simbolo in palavra:
        transicoes = [t for t in automato.transicoes if t.de == estadoAtual and t.simbolo == simbolo]
        if not transicoes:
            return False
        estadoAtual = transicoes[0].para
    return estadoAtual in automato.estadosFinais

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
