"""Prática 1 — Sistemas multitarefas usando threads.

Requer apenas Python 3.9+ e bibliotecas da instalação padrão.
O tempo de espera representa operações de entrada/saída (E/S) simuladas,
não trabalho intensivo de CPU.
"""

# Este programa demonstra o funcionamento de um sistema multitarefas
# utilizando threads em Python. Inicialmente, as tarefas são executadas
# de forma sequencial, ou seja, uma após a conclusão da outra.
# Em seguida, as mesmas tarefas são executadas de maneira concorrente,
# permitindo que seus períodos de espera se sobreponham.
#
# A biblioteca threading é utilizada para criar e controlar as threads,
# enquanto os métodos start() e join() permitem iniciar sua execução
# e aguardar sua finalização, respectivamente.
#
# O programa também utiliza a biblioteca time para medir o tempo
# necessário em cada abordagem, possibilitando comparar o desempenho.
# Além disso, demonstra como diferentes threads podem compartilhar
# informações dentro de um mesmo processo.
#
# O objetivo é compreender os conceitos de concorrência, criação,
# gerenciamento e sincronização de threads, observando como a execução
# concorrente pode melhorar o desempenho de aplicações que realizam
# operações com períodos de espera, como acesso a arquivos, redes e APIs.

import threading
import time

# Cada tarefa usa um tempo de espera simulado, em segundos.
TAREFAS = [
    ("Consulta ao sensor", 1.0),
    ("Validação dos dados", 1.0),
    ("Leitura do banco de dados", 2.0),
    ("Processamento dos dados", 5.0),
    ("Envio do relatório", 1.5),
    ("Reset do sensor", 0.5),
]


def executar_tarefa(indice, nome, duracao, resultados):
    """Simula uma E/S e grava sua resposta em uma posição exclusiva da lista."""
    thread = threading.current_thread().name
    print(f"[{thread}] Iniciou: {nome} ({duracao:.1f} s)", flush=True)
    time.sleep(duracao)  # Simula E/S sem ocupar a CPU continuamente.
    resultados[indice] = f"{nome}: concluída"
    print(f"[{thread}] Finalizou: {nome}", flush=True)


def executar_sequencial():
    resultados = [None] * len(TAREFAS)
    inicio = time.perf_counter()
    for indice, (nome, duracao) in enumerate(TAREFAS):
        executar_tarefa(indice, nome, duracao, resultados)
    return time.perf_counter() - inicio, resultados


def executar_com_threads():
    resultados = [None] * len(TAREFAS)
    threads = []
    inicio = time.perf_counter()

    # Criar: cada thread recebe os dados da própria tarefa.
    for indice, (nome, duracao) in enumerate(TAREFAS):
        thread = threading.Thread(
            target=executar_tarefa,
            args=(indice, nome, duracao, resultados),
            name=f"Thread-{indice + 1}",
        )
        threads.append(thread)

    # Iniciar todas antes de esperar: permite sobreposição das tarefas.
    for thread in threads:
        thread.start()

    # Aguardar todas: os resultados estão prontos após os join().
    for thread in threads:
        thread.join()

    return time.perf_counter() - inicio, resultados


def main():
    print("\n=== PRÁTICA 1: EXECUÇÃO SEQUENCIAL ===")
    tempo_seq, resultado_seq = executar_sequencial()
    print(f"Tempo sequencial: {tempo_seq:.2f} s")
    print("Resultados:", resultado_seq)

    print("\n=== PRÁTICA 1: EXECUÇÃO COM THREADS ===")
    tempo_thr, resultado_thr = executar_com_threads()
    print(f"Tempo com threads: {tempo_thr:.2f} s")
    print("Resultados:", resultado_thr)

    ganho = tempo_seq / tempo_thr
    print(f"\nRazão de tempos (sequencial / threads): {ganho:.2f}x")
    print("Observação: este exemplo simula tarefas limitadas por E/S, não CPU.")


if __name__ == "__main__":
    main()
