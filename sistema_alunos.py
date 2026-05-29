# Sistema de Gerenciamento de Alunos - CRUD
# Programa para criar, ler, atualizar e deletar informações de alunos

# Lista para armazenar os alunos
alunos = []

# Dicionário para rastrear o próximo número de matrícula por curso
contador_matriculas = {}


def gerar_matricula(curso):
    """
    Gera uma matrícula automática baseada no curso.
    Formato: [CURSO][NÚMERO SEQUENCIAL]
    Exemplo: GES1, GES2, GET1, etc.
    """
    if curso not in contador_matriculas:
        contador_matriculas[curso] = 1
    else:
        contador_matriculas[curso] += 1
    
    matricula = f"{curso}{contador_matriculas[curso]}"
    return matricula


def validar_email(email):
    """
    Valida se o email tem um formato básico correto.
    """
    return "@" in email and "." in email.split("@")[-1]


def criar_aluno():
    """
    Função para criar um novo aluno.
    Solicita informações ao usuário e adiciona o aluno à lista.
    """
    print("\n" + "="*50)
    print("CRIAR NOVO ALUNO")
    print("="*50)
    
    # Solicitar informações do aluno
    nome = input("Nome do aluno: ").strip()
    
    if not nome:
        print("Nome não pode estar vazio!")
        return
    
    # Verificar se o nome já existe
    if any(aluno["nome"].lower() == nome.lower() for aluno in alunos):
        print("Aluno com este nome já existe!")
        return
    
    email = input("Email do aluno: ").strip()
    
    if not validar_email(email):
        print("Email inválido! Use o formato: nome@dominio.com")
        return
    
    curso = input("Curso (GES, GEC, GET, GEP, etc.): ").strip().upper()
    
    if not curso or len(curso) < 2:
        print("Curso inválido!")
        return
    
    # Gerar matrícula automaticamente
    matricula = gerar_matricula(curso)
    
    # Criar dicionário do aluno
    novo_aluno = {
        "nome": nome,
        "email": email,
        "curso": curso,
        "matricula": matricula
    }
    
    alunos.append(novo_aluno)
    print(f"\nAluno cadastrado com sucesso!")
    print(f"   Matrícula: {matricula}")


def listar_alunos():
    """
    Função para listar todos os alunos cadastrados.
    """
    print("\n" + "="*50)
    print("LISTA DE ALUNOS")
    print("="*50)
    
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    
    print(f"\n{'Matrícula':<10} {'Nome':<20} {'Email':<25} {'Curso':<8}")
    print("-" * 65)
    
    for aluno in alunos:
        print(f"{aluno['matricula']:<10} {aluno['nome']:<20} {aluno['email']:<25} {aluno['curso']:<8}")
    
    print(f"\nTotal de alunos: {len(alunos)}")


def buscar_aluno(matricula):
    """
    Busca um aluno pela matrícula.
    Retorna o índice do aluno ou -1 se não encontrado.
    """
    for indice, aluno in enumerate(alunos):
        if aluno["matricula"] == matricula:
            return indice
    return -1


def visualizar_aluno():
    """
    Função para visualizar detalhes de um aluno específico.
    """
    print("\n" + "="*50)
    print("VISUALIZAR ALUNO")
    print("="*50)
    
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    
    matricula = input("Digite a matrícula do aluno: ").strip().upper()
    indice = buscar_aluno(matricula)
    
    if indice == -1:
        print("Aluno não encontrado!")
        return
    
    aluno = alunos[indice]
    print(f"\n{'Informações do Aluno'}:")
    print(f"  Nome: {aluno['nome']}")
    print(f"  Email: {aluno['email']}")
    print(f"  Curso: {aluno['curso']}")
    print(f"  Matrícula: {aluno['matricula']}")


def atualizar_aluno():
    """
    Função para atualizar informações de um aluno.
    """
    print("\n" + "="*50)
    print("ATUALIZAR ALUNO")
    print("="*50)
    
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    
    matricula = input("Digite a matrícula do aluno a atualizar: ").strip().upper()
    indice = buscar_aluno(matricula)
    
    if indice == -1:
        print("Aluno não encontrado!")
        return
    
    aluno = alunos[indice]
    print(f"\nAtualizando aluno: {aluno['nome']}")
    
    print("\nEscolha o que deseja atualizar:")
    print("1. Nome")
    print("2. Email")
    print("3. Curso (isso também atualizará a matrícula)")
    print("0. Cancelar")
    
    opcao = input("\nOpção: ").strip()
    
    if opcao == "1":
        novo_nome = input("Novo nome: ").strip()
        if novo_nome and not any(a["nome"].lower() == novo_nome.lower() and a != aluno for a in alunos):
            aluno["nome"] = novo_nome
            print("Nome atualizado com sucesso!")
        else:
            print("Nome inválido ou já existe!")
    
    elif opcao == "2":
        novo_email = input("Novo email: ").strip()
        if validar_email(novo_email):
            aluno["email"] = novo_email
            print("Email atualizado com sucesso!")
        else:
            print("Email inválido!")
    
    elif opcao == "3":
        novo_curso = input("Novo curso: ").strip().upper()
        if novo_curso and len(novo_curso) >= 2:
            aluno["curso"] = novo_curso
            # Gerar nova matrícula
            aluno["matricula"] = gerar_matricula(novo_curso)
            print(f"Curso atualizado com sucesso!")
            print(f"   Nova matrícula: {aluno['matricula']}")
        else:
            print("Curso inválido!")
    
    elif opcao == "0":
        print("Atualização cancelada.")
    else:
        print("Opção inválida!")


def deletar_aluno():
    """
    Função para deletar um aluno do sistema.
    """
    print("\n" + "="*50)
    print("DELETAR ALUNO")
    print("="*50)
    
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    
    matricula = input("Digite a matrícula do aluno a deletar: ").strip().upper()
    indice = buscar_aluno(matricula)
    
    if indice == -1:
        print("Aluno não encontrado!")
        return
    
    aluno = alunos[indice]
    confirmacao = input(f"\nTem certeza que deseja deletar {aluno['nome']}? (S/N): ").strip().upper()
    
    if confirmacao == "S":
        alunos.pop(indice)
        print("Aluno deletado com sucesso!")
    else:
        print("Deleção cancelada.")


def menu_principal():
    """
    Função para exibir o menu principal e controlar o fluxo do programa.
    """
    while True:
        print("\n" + "="*50)
        print("SISTEMA DE GERENCIAMENTO DE ALUNOS")
        print("="*50)
        print("1. Criar novo aluno")
        print("2. Listar todos os alunos")
        print("3. Visualizar aluno (por matrícula)")
        print("4. Atualizar informações de aluno")
        print("5. Deletar aluno")
        print("0. Sair")
        print("="*50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            criar_aluno()
        elif opcao == "2":
            listar_alunos()
        elif opcao == "3":
            visualizar_aluno()
        elif opcao == "4":
            atualizar_aluno()
        elif opcao == "5":
            deletar_aluno()
        elif opcao == "0":
            print("\nAté logo!")
            break
        else:
            print("\nOpção inválida! Tente novamente.")


# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()
