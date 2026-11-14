"""
PRÁTICA 3 — INTRODUÇÃO À MEMÓRIA DISTRIBUÍDA COM MPI
====================================================
OBJETIVO
    Demonstrar que diferentes processos possuem dados locais separados e
    cooperam para resolver um cálculo: a soma dos quadrados de 0 até N-1.

COMO FUNCIONA
    1. O processo de rank 0 cria os valores e os divide entre os ranks.
    2. scatter() distribui uma lista diferente a cada processo.
    3. Cada processo calcula a soma dos quadrados de seus próprios números.
    4. gather() devolve os resultados parciais para o rank 0.
    5. O rank 0 calcula a soma final e verifica a resposta sequencial.

PRINCIPAIS CONCEITOS E FUNÇÕES
    MPI.COMM_WORLD : grupo dos processos participantes.
    Get_rank()     : identificador do processo dentro do comunicador.
    Get_size()     : número de processos do comunicador.
    scatter()      : distribui dados do processo raiz aos demais processos.
    gather()       : reúne dados de todos os processos no processo raiz.
    MPI.Wtime()    : lê um relógio para medir intervalos de tempo locais.

EXECUÇÃO (após instalar um runtime MPI e a biblioteca mpi4py)
    mpiexec -n 4 python pratica3_memoria_distribuida.py --n 12

NOTA
    Em um computador, os processos podem executar no mesmo host, mas ainda
    têm espaços de memória separados. MPI também permite execução em nós
    distintos quando o ambiente está configurado para isso.
    O exemplo é didático: não implica ganho de desempenho com poucos dados.

    py -m pip install -r requirements.txt
    
    py -m pip install impi-rt

    mpiexec -n 4 python pratica3_memoria_distribuida.py --n 12

    Parâmetro	Significado
    mpiexec	Programa responsável por iniciar a execução paralela usando MPI.

        -n	Indica quantos processos MPI serão criados.
        4	Define que serão executados quatro processos independentes.
        python	Interpretador Python responsável por executar o código.
        pratica3_memoria_distribuida.py	Nome do arquivo Python que será executado em cada processo.
        --n	Argumento definido no próprio programa para indicar a quantidade de números utilizados no cálculo.
        12	Define que o programa trabalhará com 12 números.


        py -3.12 -m pip install -r requirements.txt

        py -3.12 -m pip install mpi4py impi-rt

        $env:Path = "$env:LOCALAPPDATA\Programs\Python\Python312\Library\bin;$env:Path"

        $env:I_MPI_ROOT = "$env:LOCALAPPDATA\Programs\Python\Python312\Library"

        py -3.12 -c "from mpi4py import MPI; print(MPI.Get_library_version())"

        mpiexec -help

        mpiexec -n 4 py -3.12 -c "from mpi4py import MPI; c=MPI.COMM_WORLD; print('Processo', c.Get_rank(), 'de', c.Get_size())"

        mpiexec -n 4 py -3.12 pratica3_memoria_distribuida.py --n 12

"""

import argparse

try:
    from mpi4py import MPI
except ImportError as erro:
    raise SystemExit(
        "mpi4py não encontrada. Instale MPI e depois execute: "
        "python -m pip install mpi4py"
    ) from erro


def dividir_dados(valores, quantidade_processos):
    """Cria uma lista por rank usando distribuição cíclica.

    Exemplo: valores = [0,1,2,3,4,5] e 3 ranks:
        rank 0 -> [0,3]
        rank 1 -> [1,4]
        rank 2 -> [2,5]
    O fatiamento [rank::quantidade_processos] evita perder elementos
    quando a quantidade total não é divisível pelo número de ranks.
    """
    return [valores[rank::quantidade_processos]
            for rank in range(quantidade_processos)]


def somar_quadrados(valores_locais):
    """Calcula SOMENTE a parcela que pertence ao processo atual."""
    return sum(numero ** 2 for numero in valores_locais)


def main():
    parser = argparse.ArgumentParser(
        description="Soma de quadrados com memória distribuída usando MPI."
    )
    parser.add_argument("--n", type=int, default=12,
                        help="Quantos números gerar: 0 até n-1 (padrão: 12).")
    args = parser.parse_args()
    if args.n < 0:
        parser.error("--n deve ser maior ou igual a zero")

    # Todos os processos executam este arquivo, mas cada um tem seu rank.
    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    total_processos = comunicador.Get_size()

    # Apenas o rank 0 mantém a lista completa no início.
    if rank == 0:
        dados = list(range(args.n))
        partes = dividir_dados(dados, total_processos)
        print(f"\n[RAIZ] {args.n} números; {total_processos} processos MPI.",
              flush=True)
    else:
        partes = None  # Os outros ranks ainda não conhecem seus dados.

    # Sincronizamos o início para medir o fluxo de comunicação/cálculo.
    comunicador.Barrier()
    inicio = MPI.Wtime()

    # scatter() entrega a cada rank somente a sua própria lista.
    meus_dados = comunicador.scatter(partes, root=0)

    # O cálculo abaixo ocorre de forma independente em cada processo.
    meu_resultado = somar_quadrados(meus_dados)

    # gather() recolhe pequenas tuplas (rank, dados locais, subtotal).
    resultados = comunicador.gather(
        (rank, meus_dados, meu_resultado), root=0
    )

    if rank == 0:
        tempo_total = MPI.Wtime() - inicio
        print("\n[RESULTADOS POR PROCESSO]")
        for rank_recebido, lista_recebida, parcial in sorted(resultados):
            print(f"  rank {rank_recebido}: dados={lista_recebida}; "
                  f"soma parcial={parcial}")

        soma_distribuida = sum(parcial for _, _, parcial in resultados)
        soma_sequencial = somar_quadrados(range(args.n))

        print(f"\n[RESULTADO DISTRIBUÍDO] {soma_distribuida}")
        print(f"[CONFERÊNCIA SEQUENCIAL] {soma_sequencial}")
        print(f"[CORRETO?] {soma_distribuida == soma_sequencial}")
        print(f"[TEMPO TOTAL (s)] {tempo_total:.6f}")
        print("[OBS.] Tempo inclui a comunicação MPI e pode variar; "
              "não use este exemplo pequeno como benchmark.\n")


if __name__ == "__main__":
    main()
