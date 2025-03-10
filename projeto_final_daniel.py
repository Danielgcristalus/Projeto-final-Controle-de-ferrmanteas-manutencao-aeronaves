import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Conexão com o banco de dados SQLite
def conectar_banco():
    conn = sqlite3.connect("ferramentas.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ferramentas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        codigo TEXT NOT NULL UNIQUE,
                        disponivel INTEGER DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        codigo TEXT NOT NULL UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS emprestimos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ferramenta_id INTEGER,
                        funcionario_id INTEGER,
                        FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id),
                        FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id))''')
    conn.commit()
    return conn

# Funções do sistema
def adicionar_ferramenta():
    nome = entry_nome_ferramenta.get()
    codigo = entry_codigo_ferramenta.get()
    if nome and codigo:
        try:
            cursor.execute("INSERT INTO ferramentas (nome, codigo) VALUES (?, ?)", (nome, codigo))
            conn.commit()
            messagebox.showinfo("Sucesso", "Ferramenta adicionada com sucesso!")
            entry_nome_ferramenta.delete(0, tk.END)
            entry_codigo_ferramenta.delete(0, tk.END)
            atualizar_listas()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código da ferramenta já existe.")
    else:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

def adicionar_funcionario():
    nome = entry_nome_funcionario.get()
    codigo = entry_codigo_funcionario.get()
    if nome and codigo:
        try:
            cursor.execute("INSERT INTO funcionarios (nome, codigo) VALUES (?, ?)", (nome, codigo))
            conn.commit()
            messagebox.showinfo("Sucesso", "Funcionário adicionado com sucesso!")
            entry_nome_funcionario.delete(0, tk.END)
            entry_codigo_funcionario.delete(0, tk.END)
            atualizar_listas()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código do funcionário já existe.")
    else:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

def emprestar_ferramenta():
    ferramenta = combo_ferramenta.get()
    funcionario = combo_funcionario.get()
    if ferramenta and funcionario:
        ferramenta_id = ferramenta.split(" - ")[0]
        funcionario_id = funcionario.split(" - ")[0]
        try:
            cursor.execute("SELECT disponivel FROM ferramentas WHERE id = ?", (ferramenta_id,))
            disponivel = cursor.fetchone()[0]
            if disponivel:
                cursor.execute("INSERT INTO emprestimos (ferramenta_id, funcionario_id) VALUES (?, ?)", (ferramenta_id, funcionario_id))
                cursor.execute("UPDATE ferramentas SET disponivel = 0 WHERE id = ?", (ferramenta_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Ferramenta emprestada com sucesso!")
                atualizar_listas()
            else:
                messagebox.showerror("Erro", "Ferramenta não está disponível.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao emprestar ferramenta: {e}")
    else:
        messagebox.showerror("Erro", "Selecione uma ferramenta e um funcionário.")

def devolver_ferramenta():
    ferramenta = combo_devolucao.get()
    if ferramenta:
        ferramenta_id = ferramenta.split(" - ")[0]
        try:
            cursor.execute("DELETE FROM emprestimos WHERE ferramenta_id = ?", (ferramenta_id,))
            cursor.execute("UPDATE ferramentas SET disponivel = 1 WHERE id = ?", (ferramenta_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Ferramenta devolvida com sucesso!")
            atualizar_listas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao devolver ferramenta: {e}")
    else:
        messagebox.showerror("Erro", "Selecione uma ferramenta para devolver.")

def atualizar_listas():
    combo_ferramenta['values'] = []
    combo_funcionario['values'] = []
    combo_devolucao['values'] = []

    cursor.execute("SELECT id, nome FROM ferramentas WHERE disponivel = 1")
    ferramentas = cursor.fetchall()
    combo_ferramenta['values'] = [f"{f[0]} - {f[1]}" for f in ferramentas]

    cursor.execute("SELECT id, nome FROM funcionarios")
    funcionarios = cursor.fetchall()
    combo_funcionario['values'] = [f"{f[0]} - {f[1]}" for f in funcionarios]

    cursor.execute("SELECT ferramentas.id, ferramentas.nome FROM ferramentas INNER JOIN emprestimos ON ferramentas.id = emprestimos.ferramenta_id")
    emprestadas = cursor.fetchall()
    combo_devolucao['values'] = [f"{f[0]} - {f[1]}" for f in emprestadas]

    atualizar_display()

def atualizar_display():
    texto_display.delete(1.0, tk.END)
    cursor.execute('''SELECT ferramentas.nome, funcionarios.nome
                      FROM emprestimos
                      INNER JOIN ferramentas ON emprestimos.ferramenta_id = ferramentas.id
                      INNER JOIN funcionarios ON emprestimos.funcionario_id = funcionarios.id''')
    emprestadas = cursor.fetchall()
    if emprestadas:
        texto_display.insert(tk.END, "Ferramentas Emprestadas:\n")
        for ferramenta, funcionario in emprestadas:
            texto_display.insert(tk.END, f"Ferramenta: {ferramenta} - Funcionário: {funcionario}\n")
    else:
        texto_display.insert(tk.END, "")

# Conexão com o banco
conn = conectar_banco()
cursor = conn.cursor()

# Interface gráfica (Tkinter)
root = tk.Tk()
root.title("Sistema de Controle de Ferramentas")

# Adicionar Ferramenta
frame_ferramenta = tk.LabelFrame(root, text="Cadastro de Ferramentas")
frame_ferramenta.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_ferramenta, text="Nome:").grid(row=0, column=0)
entry_nome_ferramenta = tk.Entry(frame_ferramenta)
entry_nome_ferramenta.grid(row=0, column=1)

tk.Label(frame_ferramenta, text="Código:").grid(row=1, column=0)
entry_codigo_ferramenta = tk.Entry(frame_ferramenta)
entry_codigo_ferramenta.grid(row=1, column=1)

tk.Button(frame_ferramenta, text="Adicionar", command=adicionar_ferramenta).grid(row=2, columnspan=2)

# Adicionar Funcionário
frame_funcionario = tk.LabelFrame(root, text="Cadastro de Funcionários")
frame_funcionario.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_funcionario, text="Nome:").grid(row=0, column=0)
entry_nome_funcionario = tk.Entry(frame_funcionario)
entry_nome_funcionario.grid(row=0, column=1)

tk.Label(frame_funcionario, text="Código:").grid(row=1, column=0)
entry_codigo_funcionario = tk.Entry(frame_funcionario)
entry_codigo_funcionario.grid(row=1, column=1)

tk.Button(frame_funcionario, text="Adicionar", command=adicionar_funcionario).grid(row=2, columnspan=2)

# Emprestar Ferramenta
frame_emprestar = tk.LabelFrame(root, text="Empréstimo de Ferramentas")
frame_emprestar.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_emprestar, text="Ferramenta:").grid(row=0, column=0)
combo_ferramenta = ttk.Combobox(frame_emprestar)
combo_ferramenta.grid(row=0, column=1)

tk.Label(frame_emprestar, text="Funcionário:").grid(row=1, column=0)
combo_funcionario = ttk.Combobox(frame_emprestar)
combo_funcionario.grid(row=1, column=1)

tk.Button(frame_emprestar, text="Emprestar", command=emprestar_ferramenta).grid(row=2, columnspan=2)

# Devolver Ferramenta
frame_devolucao = tk.LabelFrame(root, text="Devolução de Ferramentas")
frame_devolucao.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_devolucao, text="Ferramenta:").grid(row=0, column=0)
combo_devolucao = ttk.Combobox(frame_devolucao)
combo_devolucao.grid(row=0, column=1)

tk.Button(frame_devolucao, text="Devolver", command=devolver_ferramenta).grid(row=1, columnspan=2)

# Display de Ferramentas Emprestadas
frame_display = tk.LabelFrame(root, text="Ferramentas Emprestadas")
frame_display.pack(fill="both", expand="yes", padx=10, pady=10)

texto_display = tk.Text(frame_display, height=10, width=50)
texto_display.pack()

# Atualizar listas ao iniciar
atualizar_listas()

# Loop principal
root.mainloop()

