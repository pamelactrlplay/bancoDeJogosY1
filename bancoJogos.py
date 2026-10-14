import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


def inicializar_banco():
    conn = sqlite3.connect("jogos.db")
    cursor = conn.cursor()
    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jogos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    genero TEXT NOT NULL,
                    plataforma TEXT NOT NULL
                    )
    """)
    conn.commit()
    conn.close()


class AppJogos:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Banco de Dados de Jogos")
        self.root.geometry("750x520")
        self.root.config(bg="#03032f")

        inicializar_banco()

        style = ttk.Style()
        style.theme_use("clam")

        titulo_label = tk.Label(
            root,
            text="Meu catálogo de Jogos",
            font=("fantasy", 16, "bold"),
            bg="#03032f",
            fg="#7e7ef5",
        )
        titulo_label.pack(pady=10)

        form_frame = tk.LabelFrame(
            root,
            text="Adicionar novo jogo:",
            font=("fantasy", 14, "bold"),
            bg="#5c5c88",
            padx=15,
            pady=15,
        )
        form_frame.pack(fill="x", padx=20, pady=10)

        #Título do Jogo
        tk.Label(form_frame, text="Título:", font=("Arial", 10), bg="#7e7ef5").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_titulo = tk.Entry(form_frame, font=("Arial", 10), width=25)
        self.entry_titulo.grid(row=0, column=1, padx=10, pady=5)

        #Gênero
        tk.Label(form_frame, text="Gênero:", font=("Arial", 10), bg="#7e7ef5").grid(row=0, column=2, sticky="w", pady=5)
        self.combo_genero = ttk.Combobox(
            form_frame,
            values=["Terror", "Fantasia", "Ação", "Aventura", "Infantil"],
            state="readonly",
            width=15,
        )
        self.combo_genero.grid(row=0, column=3, padx=10, pady=5)
        self.combo_genero.set("Ação")  # Padrão

        #Plataforma
        tk.Label(form_frame, text="Plataforma:", font=("Arial", 10), bg="#7e7ef5").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_plataforma = tk.Entry(form_frame, font=("Arial", 10), width=25)
        self.entry_plataforma.grid(row=1, column=1, padx=10, pady=5)

        #Botão Adicionar
        btn_adicionar = tk.Button(
            form_frame,
            text="Salvar Jogo",
            bg="#0EE216",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.adicionar_jogo,
            cursor="hand2",
        )
        btn_adicionar.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        list_frame = tk.LabelFrame(
            root,
            text=" Lista de Jogos Cadastrados ",
            font=("Arial", 10, "bold"),
            bg="#5c5c88",
            padx=15,
            pady=15,
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        #Filtro por Gênero
        filter_frame = tk.Frame(list_frame, bg="#f4f4f9")
        filter_frame.pack(fill="x", pady=5)

        tk.Label(
            filter_frame, text="Filtrar por gênero:", font=("Arial", 10), bg="#f4f4f9"
        ).pack(side="left", padx=5)

        self.combo_filtro = ttk.Combobox(
            filter_frame,
            values=["Todos", "Terror", "Fantasia", "Ação", "Aventura", "Infantil"],
            state="readonly",
            width=15,
        )
        self.combo_filtro.pack(side="left", padx=5)
        self.combo_filtro.set("Todos")
        self.combo_filtro.bind("<<ComboboxSelected>>", self.filtrar_jogos)

        #Botão Excluir
        btn_remover = tk.Button(
            filter_frame,
            text="Excluir Selecionado",
            bg="#e41d0f",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.deletar_jogo,
            cursor="hand2",
        )
        btn_remover.pack(side="right", padx=5)

        #Tabela (Treeview)
        columns = ("ID", "Título", "Gênero", "Plataforma")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130 if col != "ID" else 50, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        
        self.carregar_dados()

    def adicionar_jogo(self):
        """Insere um novo jogo no banco de dados."""
        titulo = self.entry_titulo.get().strip()
        genero = self.combo_genero.get()
        plataforma = self.entry_plataforma.get().strip()

        if not titulo or not plataforma:
            messagebox.showerror("Erro", "Por favor, preencha o Título e a Plataforma!")
            return

        conn = sqlite3.connect("jogos.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jogos (titulo, genero, plataforma) VALUES (?, ?, ?)",
            (titulo, genero, plataforma),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", f"O jogo '{titulo}' foi salvo com sucesso!")
        self.entry_titulo.delete(0, tk.END)
        self.entry_plataforma.delete(0, tk.END)
        self.carregar_dados()

    def carregar_dados(self):
        """Carrega todos os registros do banco na tabela."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("jogos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jogos")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def filtrar_jogos(self, event):
        """Filtra os jogos exibidos de acordo com o gênero selecionado."""
        filtro = self.combo_filtro.get()
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("jogos.db")
        cursor = conn.cursor()

        if filtro == "Todos":
            cursor.execute("SELECT * FROM jogos")
        else:
            cursor.execute("SELECT * FROM jogos WHERE genero = ?", (filtro,))

        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def deletar_jogo(self):
        """Remove o jogo selecionado da tabela e do banco de dados."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um jogo na lista para excluir.")
            return

        item_values = self.tree.item(selected_item, "values")
        jogo_id = item_values[0]
        jogo_titulo = item_values[1]

        resposta = messagebox.askyesno(
            "Confirmação", f"Tem certeza que deseja excluir o jogo '{jogo_titulo}'?"
        )
        if resposta:
            conn = sqlite3.connect("jogos.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jogos WHERE id = ?", (jogo_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Jogo excluído com sucesso!")
            self.carregar_dados()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppJogos(root)
    root.mainloop()