import sqlite3
import bcrypt

def criptografia_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

def verifica_senha(senha_hash, senha):
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash)

def criar_conta(criacao_cargo): #Só o admin(chefe) e um usuario que é funcionario podem criar contas.
    if criacao_cargo not in ['admin', 'user']:
        print("Você não tem permissão para isso.")
        return

    conn = sqlite3.connect('livraria_nina.db')
    cursor = conn.cursor()

    usuario = input("Digite um nome de usuário: ")
    senha = input("Digite uma senha: ")
    senha_hash = criptografia_senha(senha)

    cursor.execute("SELECT * FROM cargos WHERE nome IN ('user', 'cliente')")
    cargos = cursor.fetchall()
    print("Cargos disponíveis:")
    for cargo in cargos:
        print(f"{cargo[0]} - {cargo[1]}")

    cargo = int(input("Escolha o ID do cargo desejado: "))

    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (usuario, senha_hash, cargo))
        conn.commit()
        print("Conta criada com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: nome de usuário já existe.")
    finally:
        conn.close()

def busca():
    conn = sqlite3.connect('livraria_nina.db')
    cursor = conn.cursor()

    print("\nOpções de pesquisa:")
    print("1. Pesquisar por título")
    print("2. Pesquisar por autor")
    opcao = input("Escolha uma opção: ")

    if opcao == '1':
        title = input("Digite o título do livro: ")
        cursor.execute("SELECT * FROM livros WHERE titulo LIKE ?", ('%' + title + '%',))
    elif opcao == '2':
        author = input("Digite o nome do autor: ")
        cursor.execute("SELECT * FROM livros WHERE autor LIKE ?", ('%' + author + '%',))
    else:
        print("Opção inválida.")
        conn.close()
        return

    resultado = cursor.fetchall()
    if resultado:
        print("\nLivros encontrados:")
        for livro in resultado:
            print(f"ID: {livro[0]}, Título: {livro[4]}, Autor: {livro[2]}, Editora: {livro[1]}, Ano: {livro[3]}, Preço: {livro[5]:.2f}, Estoque: {livro[6]}")
    else:
        print("Nenhum livro encontrado com as informações que você passou.")

    conn.close()

def novo_livro():
    """Permite só o chefe adicionar os livros novos."""
    conn = sqlite3.connect('livraria_nina.db')
    cursor = conn.cursor()

    editora = input("Digite a editora: ")
    autor = input("Digite o autor: ")
    ano = int(input("Digite o ano de publicação: "))
    titulo = input("Digite o título do livro: ")
    preco = float(input("Digite o preço: "))
    estoque = int(input("Digite a quantidade em estoque: "))

    try:
        cursor.execute(""" 
            INSERT INTO livros (editora, autor, ano, titulo, preco, estoque)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (editora, autor, ano, titulo, preco, estoque))
        conn.commit()
        print("Livro adicionado.")
    except sqlite3.IntegrityError:
        print("Erro: Já existe um livro com esse título em nosso sistema.")
    finally:
        conn.close()

def apagar_livro(): #Permite ao chefe excluir um livro do banco de dados.
    conn = sqlite3.connect('livraria_nina.db')
    cursor = conn.cursor()

    id_livro = input("Digite o ID do livro que deseja excluir: ")
    cursor.execute("SELECT titulo FROM livros WHERE id = ?", (id_livro,))
    resultado = cursor.fetchone()

    if resultado:
        titulo = resultado[0]
        confirmacao = input(f"Tem certeza de que deseja excluir o livro '{titulo}'? (s/n): ").lower()
        if confirmacao == 's':
            cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
            conn.commit()
            print(f"O livro '{titulo}' foi excluído com sucesso do sistema da livraria.")
        else:
            print("Operação de exclusão cancelada.")
    else:
        print("Livro não encontrado.")
    conn.close()


def marcar_fora_estoque(id_usuario): #Marca um livro como fora de estoque e registra o interesse do usuário.
    conn = sqlite3.connect('livraria_nina.db')
    cursor = conn.cursor()
    id_livro = int(input("Digite o ID do livro fora de estoque: "))
    cursor.execute("SELECT * FROM livros WHERE id = ? AND estoque = 0", (id_livro,))
    livro = cursor.fetchone()

    if livro:
        cursor.execute("INSERT INTO pedidos_fora_estoque (id_livro, id_usuario, data_pedido) VALUES (?, ?, datetime('now'))", (id_livro, id_usuario))
        conn.commit()
        print(f"Seu interesse pelo livro '{livro[4]}' foi registrado em nossa livraria.")
    else:
        print("Este livro não está fora de estoque ou não existe.")

    conn.close()

def menu_de_acesso(cargo, id_usuario): #Menu baseado no tipo de usuario
    while True:
        print("\nOpções disponíveis:")
        if cargo == 'admin':
            print("1. Adicionar livro\n2. Excluir livro\n3. Pesquisar livro\n4. Criar usuário\n5. Sair")
            opcao = input("Escolha uma opção: ")
            if opcao == '1':
                novo_livro()
            elif opcao == '2':
                apagar_livro()
            elif opcao == '3':
                busca()
            elif opcao == '4':
                criar_conta('admin')
            elif opcao == '5':
                print("Obrigado por usar o sistema da Livraria Nina! Volte sempre!")
                break
            else:
                print("Opção inválida.")

        elif cargo == 'user':
            print("1. Pesquisar livro\n2. Registrar interesse em livro fora de estoque\n3. Criar usuário\n4. Sair")
            opcao = input("Escolha uma opção: ")
            if opcao == '1':
                busca()
            elif opcao == '2':
                marcar_fora_estoque(id_usuario)
            elif opcao == '3':
                criar_conta('user')
            elif opcao == '4':
                print("Obrigado por usar o sistema da Livraria Nina! Volte sempre!")
                break
            else:
                print("Opção inválida.")

        elif cargo == 'cliente':
            print("1. Pesquisar livro\n2. Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                busca()
            elif opcao == '2':
                print("Obrigado por usar o sistema da Livraria Nina! Volte sempre!")
                break
            else:
                print("Opção inválida.")

def iniciar_livraria():
    print("\nBem-vindo(a) ao Sistema de Gestão da Livraria Nina! Onde conhecimento é a nossa paixão.")
    while True:
        print("\n1. Login\n2. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            usuario = input("Digite seu nome de usuário: ")
            senha = input("Digite sua senha: ")

            conn = sqlite3.connect('livraria_nina.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id, senha, cargo FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()

            if resultado and verifica_senha(resultado[1], senha):
                id_usuario = resultado[0]
                cargo_id = resultado[2]
                cursor.execute("SELECT nome FROM cargos WHERE id = ?", (cargo_id,))
                cargo = cursor.fetchone()[0]
                print(f"\nBem-vindo, {usuario}!")
                menu_de_acesso(cargo, id_usuario)
            else:
                print("Usuário ou senha inválidos.")
            conn.close()

        elif opcao == '2':
            print("Obrigado por usar o sistema da Livraria Nina! Volte sempre!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    iniciar_livraria()