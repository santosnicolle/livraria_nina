import sqlite3
import bcrypt

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    # Criando a tabela de roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    ''')

    # Criando a tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password CHAR(60) NOT NULL,
            role_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    ''')

    # Inserir roles padrão se não existirem
    cursor.execute("INSERT OR IGNORE INTO roles (name) VALUES ('admin'), ('user'), ('cliente')")

    conn.commit()
    conn.close()

def init_bookstore_db():
    """Inicializa o banco de dados da livraria com a tabela de livros."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    # Criando a tabela de livros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher VARCHAR(100) NOT NULL,
            author VARCHAR(100) NOT NULL,
            year INTEGER NOT NULL,
            title VARCHAR(200) UNIQUE NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password):
    """Gera o hash para uma senha."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, password):
    """Verifica uma senha em relação ao hash armazenado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def create_account():
    """Permite que um novo usuário crie uma conta."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    username = input("Digite um nome de usuário: ")
    password = input("Digite uma senha: ")
    hashed_password = hash_password(password)

    # Exibindo as roles disponíveis
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    print("Roles disponíveis:")
    for role in roles:
        print(f"{role[0]} - {role[1]}")

    role_id = int(input("Escolha o ID da role desejada: "))

    try:
        cursor.execute("INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)", (username, hashed_password, role_id))
        conn.commit()
        print("Conta criada com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: nome de usuário já existe.")
    finally:
        conn.close()

def add_book():
    """Adiciona um novo livro ao banco de dados."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    publisher = input("Editora: ")
    author = input("Nome do autor: ")
    year = int(input("Ano de publicação: "))
    title = input("Título do livro: ")
    price = float(input("Preço: "))
    stock = int(input("Quantidade em estoque: "))

    try:
        cursor.execute(
            "INSERT INTO books (publisher, author, year, title, price, stock) VALUES (?, ?, ?, ?, ?, ?)",
            (publisher, author, year, title, price, stock)
        )
        conn.commit()
        print("Livro adicionado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: o título do livro já existe.")
    finally:
        conn.close()

def delete_book():
    """Exclui um livro do banco de dados."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    title = input("Digite o título do livro a ser excluído: ")
    cursor.execute("DELETE FROM books WHERE title = ?", (title,))

    if cursor.rowcount > 0:
        conn.commit()
        print("Livro excluído com sucesso!")
    else:
        print("Livro não encontrado.")

    conn.close()

def search_books():
    """Permite a pesquisa de livros."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    query = input("Digite o título, autor ou editora para buscar: ")
    cursor.execute(
        "SELECT title, author, publisher, year, price, stock FROM books WHERE title LIKE ? OR author LIKE ? OR publisher LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )

    results = cursor.fetchall()
    if results:
        for book in results:
            print(f"Título: {book[0]}, Autor: {book[1]}, Editora: {book[2]}, Ano: {book[3]}, Preço: {book[4]}, Estoque: {book[5]}")
    else:
        print("Nenhum livro encontrado.")

    conn.close()

def mark_out_of_stock():
    """Sinaliza que um cliente deseja um livro fora de estoque."""
    conn = sqlite3.connect('user_management.db')
    cursor = conn.cursor()

    title = input("Digite o título do livro desejado: ")
    cursor.execute("SELECT stock FROM books WHERE title = ?", (title,))
    result = cursor.fetchone()

    if result is None:
        print("Livro não encontrado.")
    elif result[0] > 0:
        print("O livro está em estoque.")
    else:
        print("Pedido registrado: livro fora de estoque.")

    conn.close()

def user_menu(role):
    """Exibe o menu baseado no papel do usuário."""
    while True:
        print("\nOpções disponíveis:")
        if role == 'admin':
            print("1. Adicionar livro\n2. Excluir livro\n3. Pesquisar livro\n4. Sair")
            choice = input("Escolha uma opção: ")

            if choice == '1':
                add_book()
            elif choice == '2':
                delete_book()
            elif choice == '3':
                search_books()
            elif choice == '4':
                break
            else:
                print("Opção inválida.")

        elif role == 'user':
            print("1. Pesquisar livro\n2. Registrar interesse em livro fora de estoque\n3. Atualizar informações de livro\n4. Sair")
            choice = input("Escolha uma opção: ")

            if choice == '1':
                search_books()
            elif choice == '2':
                mark_out_of_stock()
            elif choice == '3':
                add_book()
            elif choice == '4':
                break
            else:
                print("Opção inválida.")

        elif role == 'cliente':
            print("1. Pesquisar livro\n2. Registrar interesse em livro fora de estoque\n3. Sair")
            choice = input("Escolha uma opção: ")

            if choice == '1':
                search_books()
            elif choice == '2':
                mark_out_of_stock()
            elif choice == '3':
                break
            else:
                print("Opção inválida.")

def main():
    """Função principal para controle do programa."""
    init_db()
    init_bookstore_db()

    while True:
        print("\n1. Fazer login\n2. Criar conta\n3. Sair")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            username = input("Usuário: ")
            password = input("Senha: ")

            conn = sqlite3.connect('user_management.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT u.password, r.name FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.username = ?
            """, (username,))
            result = cursor.fetchone()

            if result and check_password(result[0], password):
                print(f"Bem-vindo, {username}! ({result[1]})")
                user_menu(result[1])
            else:
                print("Credenciais inválidas.")
            conn.close()

        elif choice == '2':
            create_account()
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
