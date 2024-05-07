from tkinter import *
from tkinter import messagebox, filedialog
import pyodbc
import base64

# Conectar ao banco de dados
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-G7JP4L7\SQLEXPRESS;DATABASE=aeroporto;UID='';PWD=''')


def selecionar_arquivo():
    caminho_arquivo = filedialog.askopenfilename()
    entry_arquivo.delete(0, 'end')
    entry_arquivo.insert(0, caminho_arquivo)

def converter_imagem_para_base64(caminho_imagem):
    with open(caminho_imagem, 'rb') as arquivo_imagem:
        imagem_base64 = base64.b64encode(arquivo_imagem.read()).decode('utf-8')
    return imagem_base64

def fazer_reserva():
    # Função para fazer a reserva do assento
    numero_voo = entry_voo.get()
    numero_assento = entry_assento.get().upper()  # Convertendo para maiúsculas
    nome_passageiro = entry_nome.get()
    caminho_arquivo = entry_arquivo.get()

    print("Número do Voo:", numero_voo)
    print("Número do Assento:", numero_assento)
    print("Caminho do Arquivo:", caminho_arquivo)  # Verificar o caminho do arquivo

    cursor = conn.cursor()
    try:
        # Obter o ID do assento
        query = "SELECT id FROM Assentos WHERE numero_assento = ? AND id_voo = (SELECT id FROM Voos WHERE numero_voo = ?)"
        print("Consulta SQL:", query)
        cursor.execute(query, (numero_assento, numero_voo))
        row = cursor.fetchone()
        print("Resultado da consulta:", row)
        if row is None:
            messagebox.showerror("Erro", f"Nenhum assento encontrado para o voo {numero_voo} e o assento {numero_assento}.")
        else:
            id_assento = int(row[0])  # Convertendo para inteiro
            # Verificar se o assento está disponível
            cursor.execute("SELECT disponivel FROM Assentos WHERE id = ?", (id_assento,))
            disponibilidade = cursor.fetchone()[0]
            if disponibilidade == 0:
                messagebox.showerror("Erro", "Assento já está reservado.")
            else:
                # Fazer a reserva
                imagem_base64 = converter_imagem_para_base64(caminho_arquivo)
                # Inserir os dados na tabela Reservas
                cursor.execute("""
                    INSERT INTO Reservas (id_voo, id_assento, nome_passageiro, imgreserva)
                    VALUES (?, ?, ?, ?)
                """, (numero_voo, id_assento, nome_passageiro, imagem_base64))
                # Atualizar a disponibilidade do assento
                cursor.execute("UPDATE Assentos SET disponivel = 0 WHERE id = ?", (id_assento,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Reserva realizada com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao executar consulta SQL: {query}\n{str(e)}")
    finally:
        cursor.close()




# Interface Gráfica
root = Tk()
root.title("Reserva de Assento")
root.geometry("400x200")

label_voo = Label(root, text="Número do Voo:")
label_voo.grid(row=0, column=0, padx=10, pady=5)
entry_voo = Entry(root)
entry_voo.grid(row=0, column=1, padx=10, pady=5)

label_assento = Label(root, text="Número do Assento:")
label_assento.grid(row=1, column=0, padx=10, pady=5)
entry_assento = Entry(root)
entry_assento.grid(row=1, column=1, padx=10, pady=5)

label_nome = Label(root, text="Nome do Passageiro:")
label_nome.grid(row=2, column=0, padx=10, pady=5)
entry_nome = Entry(root)
entry_nome.grid(row=2, column=1, padx=10, pady=5)

label_arquivo = Label(root, text="Comprovante do ticket:")
label_arquivo.grid(row=3, column=0, padx=10, pady=5)
entry_arquivo = Entry(root)
entry_arquivo.grid(row=3, column=1, padx=10, pady=5)

botao_selecionar_arquivo = Button(root, text="Selecionar Arquivo", command=selecionar_arquivo)
botao_selecionar_arquivo.grid(row=3, column=2, padx=10, pady=5)

botao_fazer_reserva = Button(root, text="Fazer Reserva", command=fazer_reserva)
botao_fazer_reserva.grid(row=4, column=1, padx=10, pady=5)

root.mainloop()