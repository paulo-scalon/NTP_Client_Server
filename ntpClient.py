import socket
import struct
import time
import tkinter as tk
from tkinter import messagebox

NTP_PORT = 123
DELTA_TIMESTAMP_NTP = 2208988800  # Ajuste do epoch NTP (1900) para o epoch Unix (1970)
DEFAULT_NTP_SERVER = 'time.google.com'
FUSO_HORARIO = -3  # Ajuste para o seu fuso horário (exemplo: -3 para GMT-3)

class NTPClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Cliente NTP")
        self.master.geometry("500x300")  # Define o tamanho da janela

        # Configuração de fonte maior
        font = ('Arial', 14)
        
        self.label = tk.Label(master, text="Servidor NTP:", font=font)
        self.label.pack(pady=10)  # Espaçamento vertical

        self.entry = tk.Entry(master, font=font, width=30)
        self.entry.pack(pady=10)  # Espaçamento vertical
        self.entry.insert(0, DEFAULT_NTP_SERVER)
        
        self.button = tk.Button(master, text="Obter Hora", command=self.get_time, font=font)
        self.button.pack(pady=20)  # Espaçamento vertical maior
        
        self.result_label = tk.Label(master, text="Horário: ", font=font)
        self.result_label.pack(pady=5)  # Espaçamento vertical

        self.offset_label = tk.Label(master, text="Offset: ", font=font)
        self.offset_label.pack(pady=5)  # Espaçamento vertical

        self.delay_label = tk.Label(master, text="Delay: ", font=font)
        self.delay_label.pack(pady=5)  # Espaçamento vertical

    def get_time(self):
        server = self.entry.get()
        try:
            time_data, offset, delay = self.request_time(server)
            self.result_label.config(text=f"Horário: {time_data}")
            self.offset_label.config(text=f"Offset: {offset:.6f} segundos")
            self.delay_label.config(text=f"Delay: {delay:.6f} segundos")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível obter o tempo: {e}")

    def request_time(self, server):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)  # Timeout de 5 segundos
            addr = (server, NTP_PORT)

            # Construção do pacote NTP (Modo 3 - Cliente)
            solicitacao = struct.pack(
                "!B B B b 3I 8I",
                0b00100011,  # Leap Indicator (0), Versão (4), Modo (3 - Cliente)
                0,  # Estrato (não usado pelo cliente)
                0,  # Intervalo de Poll
                -6,  # Precisão (-6 ≈ 15.6ms)
                0, 0, 0,  # Root Delay, Root Dispersion, Reference ID
                0, 0,  # Timestamp de Referência (segundos, fração)
                0, 0,  # Timestamp de Origem (segundos, fração)
                0, 0,  # Timestamp de Recebimento (segundos, fração)
                0, 0   # Timestamp de Transmissão (segundos, fração)
            )

            # Enviar solicitação NTP
            timestamp_origem = time.time()  # Tempo de envio da solicitação
            sock.sendto(solicitacao, addr)

            # Receber resposta
            dados, _ = sock.recvfrom(48)  # Receber resposta de 48 bytes
            timestamp_destino = time.time()  # Tempo em que a resposta chegou

            # Desempacotar a resposta NTP
            desempacotado = struct.unpack("!12I", dados)
            segundos_transmissao = desempacotado[10]  # Timestamp de Transmissão
            fracao_transmissao = desempacotado[11]  # Timestamp de Transmissão (fração)

            # Converter para tempo Unix
            timestamp_transmissao = segundos_transmissao - DELTA_TIMESTAMP_NTP + (fracao_transmissao / (2**32))

            # Calcular offset e delay
            offset = ((timestamp_transmissao - timestamp_origem) + (timestamp_transmissao - timestamp_destino)) / 2
            delay = (timestamp_destino - timestamp_origem) - (timestamp_transmissao - timestamp_origem)

            # Ajustar a hora para o horário correto (considerando o fuso horário)
            timestamp_local = timestamp_transmissao + (FUSO_HORARIO * 3600)

            # Formatando a hora local
            time_data = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp_local))

            return time_data, offset, delay

if __name__ == "__main__":
    root = tk.Tk()
    app = NTPClient(root)
    root.mainloop()
