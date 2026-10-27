"""Prática 2 — Condição de corrida e controle por Lock.

Usa um atraso pequeno entre a leitura e a escrita para tornar a
condição de corrida visível e reproduzível na atividade didática.
O atraso NÃO é necessário em código de produção.
"""

# Este programa demonstra como múltiplas threads podem acessar e
# modificar um mesmo recurso compartilhado, utilizando como exemplo
# uma variável que funciona como contador.
#
# Inicialmente, as threads realizam incrementos sem qualquer mecanismo
# de proteção. Como o incremento envolve operações de leitura,
# modificação e escrita, podem ocorrer condições de corrida (race
# conditions), nas quais diferentes threads interferem umas nas outras,
# ocasionando a perda de atualizações e resultados incorretos.
#
# Para evidenciar esse comportamento, o programa introduz pequenos
# atrasos entre a leitura e a atualização do contador.
#
# Posteriormente, é utilizado um objeto Lock da biblioteca threading,
# responsável por garantir que apenas uma thread por vez execute a
# seção crítica do programa. Dessa forma, o recurso compartilhado
# passa a ser atualizado de maneira controlada e consistente.
#
# O objetivo é compreender os problemas associados ao compartilhamento
# de memória entre threads e a importância dos mecanismos de
# sincronização para garantir a integridade dos dados, evitando
# condições de corrida e reduzindo os riscos de inconsistências.
#
# O exemplo também permite discutir deadlocks, situações em que threads
# ficam bloqueadas aguardando recursos umas das outras, destacando
# a importância do uso correto e da liberação adequada dos locks.

import threading
import time

NUM_THREADS = 8
INCREMENTOS_POR_THREAD = 1000
ATRASO_DIDATICO = 0.00001

contador = 0  # Recurso compartilhado por todas as threads.
lock = threading.Lock()


def incrementar_sem_lock():
    """ERRO proposital: a operação ler-modificar-escrever não é protegida."""
    global contador
    for _ in range(INCREMENTOS_POR_THREAD):
        valor_antigo = contador
        time.sleep(ATRASO_DIDATICO)  # Aumenta chance de outra thread interferir.
        contador = valor_antigo + 1


def incrementar_com_lock():
    """CORRETO: apenas uma thread altera o contador de cada vez."""
    global contador
    for _ in range(INCREMENTOS_POR_THREAD):
        with lock:  # O lock é liberado automaticamente ao sair do bloco.
            valor_antigo = contador
            time.sleep(ATRASO_DIDATICO)  # Somente para comparação didática.
            contador = valor_antigo + 1


def executar_teste(funcao):
    global contador
    contador = 0
    threads = [
        threading.Thread(target=funcao, name=f"Thread-{i + 1}")
        for i in range(NUM_THREADS)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return contador


def main():
    esperado = NUM_THREADS * INCREMENTOS_POR_THREAD
    print("\n=== PRÁTICA 2: RECURSO COMPARTILHADO ===")
    print(f"Threads: {NUM_THREADS}")
    print(f"Incrementos por thread: {INCREMENTOS_POR_THREAD}")
    print(f"Resultado esperado: {esperado}\n")

    sem_protecao = executar_teste(incrementar_sem_lock)
    print(f"Sem Lock: {sem_protecao} (esperado: {esperado})")

    com_protecao = executar_teste(incrementar_com_lock)
    print(f"Com Lock: {com_protecao} (esperado: {esperado})")

    print("\nPor que join() não resolve a condição de corrida?")
    print("Porque join() apenas aguarda o fim das threads; Lock controla o acesso.")
    print("Atenção: o valor sem Lock pode variar a cada execução.")


if __name__ == "__main__":
    main()
