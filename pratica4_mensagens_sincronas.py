"""
PRÁTICA 4 — TROCA DE MENSAGENS SÍNCRONAS COM MPI
================================================
OBJETIVO
    Mostrar, com DOIS processos, que Ssend() é um envio síncrono: a chamada
    de envio só termina quando uma recepção correspondente foi iniciada.

COMO FUNCIONA
    1. O rank 0 prepara um número inteiro (por padrão, 21).
    2. O rank 1 aguarda um tempo configurável ANTES de receber o número.
    3. O rank 0 chama Ssend(): fica bloqueado até o rank 1 iniciar Recv().
    4. O rank 1 transforma o número: resposta = 2 * valor + 1.
    5. O rank 1 devolve a resposta com Ssend() e o rank 0 usa Recv().
    6. O rank 0 apresenta a resposta e a duração do primeiro Ssend().

PRINCIPAIS FUNÇÕES
    MPI.COMM_WORLD : comunicador entre os processos MPI.
    Get_rank()     : identifica se o processo é 0 ou 1.
    Barrier()      : alinha o início do exercício; NÃO realiza o Ssend.
    Ssend()        : envio BLOQUEANTE em modo SÍNCRONO.
    Recv()         : recepção bloqueante do buffer correspondente.
    MPI.Wtime()    : mede a duração da chamada de envio.

    Métodos com MAIÚSCULAS Ssend/Recv recebem buffers NumPy diretamente.
    A mensagem é identificada por origem, destino, comunicador e tag.

EXECUÇÃO
    mpiexec -n 2 python pratica4_mensagens_sincronas.py --valor 21 --atraso 1.0

ATENÇÃO
    'Bloqueante' não significa necessariamente 'síncrono'. Send() pode
    completar de forma diferente conforme implementação e tamanho da
    mensagem; Ssend() garante o handshake com a recepção correspondente.
    Não execute com mais ou menos de 2 processos neste exercício.
"""

import argparse
import time

try:
    import numpy as np
    from mpi4py import MPI
except ImportError as erro:
    raise SystemExit(
        "Instale NumPy e mpi4py com: python -m pip install numpy mpi4py"
    ) from erro

# Tags distinguem os dois sentidos da comunicação.
TAG_PERGUNTA = 101
TAG_RESPOSTA = 202


def calcular_resposta(valor):
    """Transformação realizada apenas pelo processo receptor (rank 1)."""
    return 2 * valor + 1


def main():
    parser = argparse.ArgumentParser(
        description="Demonstra envio síncrono MPI com Ssend e Recv."
    )
    parser.add_argument("--valor", type=int, default=21,
                        help="Número enviado do rank 0 ao rank 1.")
    parser.add_argument("--atraso", type=float, default=1.0,
                        help="Segundos que o rank 1 espera antes de Recv().")
    args = parser.parse_args()
    if args.atraso < 0:
        parser.error("--atraso não pode ser negativo")

    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    quantidade = comunicador.Get_size()

    # Todos os processos recebem o mesmo parâmetro -n do mpiexec.
    if quantidade != 2:
        if rank == 0:
            print("ERRO: esta atividade exige exatamente dois processos. "
                  "Use: mpiexec -n 2 python pratica4_mensagens_sincronas.py")
        return

    # Faz os dois ranks começarem a demonstração no mesmo ponto lógico.
    comunicador.Barrier()

    if rank == 0:
        # Um NumPy array de 64 bits funciona como buffer de envio MPI.
        mensagem = np.array([args.valor], dtype=np.int64)
        resposta = np.empty(1, dtype=np.int64)

        print(f"[rank 0] Tentando enviar {mensagem[0]} com Ssend...",
              flush=True)
        inicio = MPI.Wtime()

        # Importante: Ssend() precisa da recepção correspondente no rank 1.
        comunicador.Ssend([mensagem, MPI.INT64_T],
                          dest=1, tag=TAG_PERGUNTA)

        duracao = MPI.Wtime() - inicio
        print(f"[rank 0] Ssend retornou após {duracao:.3f} s.",
              flush=True)

        # A resposta usa outra tag, evitando confundir as duas mensagens.
        comunicador.Recv([resposta, MPI.INT64_T],
                         source=1, tag=TAG_RESPOSTA)
        print(f"[rank 0] Resposta recebida: {int(resposta[0])}.",
              flush=True)
        print(f"[rank 0] Conferência: "
              f"{int(resposta[0]) == calcular_resposta(args.valor)}",
              flush=True)

    else:  # rank == 1
        recebida = np.empty(1, dtype=np.int64)
        print(f"[rank 1] Esperando {args.atraso:.2f} s "
              "ANTES de chamar Recv...", flush=True)
        time.sleep(args.atraso)

        # Esta chamada realiza o pareamento com Ssend() do rank 0.
        comunicador.Recv([recebida, MPI.INT64_T],
                         source=0, tag=TAG_PERGUNTA)
        valor_recebido = int(recebida[0])
        print(f"[rank 1] Mensagem recebida: {valor_recebido}.",
              flush=True)

        novo_valor = calcular_resposta(valor_recebido)
        devolucao = np.array([novo_valor], dtype=np.int64)
        print(f"[rank 1] Enviando de volta {novo_valor} com Ssend...",
              flush=True)

        # O rank 0, depois de concluir o Ssend inicial, espera a resposta.
        comunicador.Ssend([devolucao, MPI.INT64_T],
                          dest=0, tag=TAG_RESPOSTA)
        print("[rank 1] Resposta entregue.", flush=True)


if __name__ == "__main__":
    main()
