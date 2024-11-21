import sqlite3
from datetime import date

def conectar_banco():
    conn = sqlite3.connect("livraria.db")
    return conn

def adicionar_livro(titulo, autor, editora, quantidade_em_estoque, preco):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Livros (titulo, autor, editora, quantidade_em_estoque, preco)
        VALUES (?, ?, ?, ?, ?)
    """, (titulo, autor, editora, quantidade_em_estoque, preco))
    conn.commit()
    conn.close()

def registrar_venda(id_livro, quantidade):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Vendas (id_livro, quantidade, data_venda)
        VALUES (?, ?, ?)
    """, (id_livro, quantidade, date.today()))
    cursor.execute("""
        UPDATE Livros
        SET quantidade_em_estoque = quantidade_em_estoque - ?
        WHERE id = ?
    """, (quantidade, id_livro))
    conn.commit()
    conn.close()

def adicionar_pedido(id_livro, quantidade, status="Pendente"):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Pedidos (id_livro, quantidade, data_pedido, status)
        VALUES (?, ?, ?, ?)
    """, (id_livro, quantidade, date.today(), status))
    conn.commit()
    conn.close()

def consultar_estoque():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Livros")
    livros = cursor.fetchall()
    conn.close()
    return livros

def buscar_livros_por_editora(editora):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Livros WHERE editora = ?", (editora,))
    livros = cursor.fetchall()
    conn.close()
    return livros

def livros_com_estoque_baixo(limite=5):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Livros WHERE quantidade_em_estoque < ?", (limite,))
    livros = cursor.fetchall()
    conn.close()
    return livros

#adicionar login - com autenticação

if __name__ == "__main__":
    # Adicionando um livro com editora
    adicionar_livro("O livro grande", "J.R.R. Tolkien", "Martins Fontes", 10, 39.90)

    # Registrando uma venda
    registrar_venda(1, 2)

    # Adicionando um pedido
    adicionar_pedido(1, 5)

    # Consultando o estoque
    print("Estoque atual:")
    for livro in consultar_estoque():
        print(livro)

    # Buscando livros por editora
    print("\nLivros da editora 'Martins Fontes':")
    for livro in buscar_livros_por_editora("Martins Fontes"):
        print(livro)

    # Livros com estoque baixo
    print("\nLivros com estoque baixo:")
    for livro in livros_com_estoque_baixo():
        print(livro)
