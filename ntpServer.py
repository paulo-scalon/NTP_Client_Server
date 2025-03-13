import socket
import struct
import time

NTP_PORT = 123
NTP_TIMESTAMP_DELTA = 2208988800  # Offset entre 1900 e 1970

def servidorNtp():
    # Cria o socket UDP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind(("0.0.0.0", NTP_PORT))  # Ouvindo em todas as interfaces na porta 123

    print(f"Servidor NTP em execução na porta {NTP_PORT}...")

    while True:
        # Espera por dados de um cliente
        dados, endereco = servidor.recvfrom(48)  # O tamanho do pacote NTP é fixo em 48 bytes
        timestampRecebido = time.time() + NTP_TIMESTAMP_DELTA  # Tempo de recebimento (NTP)

        # Extrai o timestamp de origem do cliente (de onde veio a solicitação)
        timestampOrigem = struct.unpack("!Q", dados[24:32])[0]
        timestampOrigem = timestampOrigem - NTP_TIMESTAMP_DELTA  # Ajusta para o epoch Unix

        # Ajusta o timestamp de origem para garantir que ele esteja dentro do limite
        if timestampOrigem < 0:
            timestampOrigem = 0

        # Calcula o timestamp de transmissão (tempo atual do servidor)
        timestampTransmissao = time.time() + NTP_TIMESTAMP_DELTA

        # Converte os timestamps para inteiros e fração de segundos
        secs_transmissao = int(timestampTransmissao)
        frac_transmissao = int((timestampTransmissao - secs_transmissao) * (2**32))

        secs_origem = int(timestampOrigem)
        frac_origem = int((timestampOrigem - secs_origem) * (2**32))

        secs_recebido = int(timestampRecebido)
        frac_recebido = int((timestampRecebido - secs_recebido) * (2**32))

        try:
            # Monta resposta NTP (modo 4 - servidor)
            resposta = struct.pack(
                "!B B B b 11I",
                0b00100100,  # Leap Indicator (0), Versão (4), Modo (4 - Servidor)
                1,  # Stratum (1 - Primário)
                0,  # Poll Interval
                -6,  # Precision (-6 ≈ 15.6ms)
                0,  # Root Delay
                0,  # Root Dispersion
                0x4C4C4F43,  # Reference ID (pode ser um identificador qualquer, como "LOCL")
                secs_transmissao, frac_transmissao,  # Reference Timestamp
                secs_origem, frac_origem,  # Origem (cliente)
                secs_recebido, frac_recebido,  # Recebimento (servidor)
                secs_transmissao, frac_transmissao  # Transmissão (servidor)
            )
        except struct.error as e:
            print(f"Erro ao empacotar resposta: {e}")
            continue

        # Envia a resposta ao cliente
        servidor.sendto(resposta, endereco)
        print(f"Respondendo ao cliente {endereco} com a hora: {time.ctime(timestampTransmissao)}")

if __name__ == "__main__":
    servidorNtp()
