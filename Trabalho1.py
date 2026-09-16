from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Dict


@dataclass
class Livro:
    titulo: str
    codigo: str
    copias_disponiveis: int = 1
    fila_espera: List["Aluno"] = field(default_factory=list)

    def disponivel(self) -> bool:
        return self.copias_disponiveis > 0from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Dict


@dataclass
class Livro:
    titulo: str
    codigo: str
    copias_disponiveis: int = 1
    fila_espera: List["Aluno"] = field(default_factory=list)

    def disponivel(self) -> bool:
        return self.copias_disponiveis > 0


@dataclass
class Aluno:
    nome: str
    matricula: str
    emprestimos: List["Emprestimo"] = field(default_factory=list)
    multas_pendentes: float = 0.0

    def emprestimos_ativos(self) -> List["Emprestimo"]:
        return [e for e in self.emprestimos if e.status == "ativo"]

    def possui_multa(self) -> bool:
        return self.multas_pendentes > 0


@dataclass
class Emprestimo:
    aluno: Aluno
    livro: Livro
    data_emprestimo: date
    data_devolucao_prevista: date
    status: str = "ativo"


class SistemaBiblioteca:
    MAX_LIVROS_POR_ALUNO = 5
    PRAZO_EMPRESTIMO_DIAS = 14
    MULTA_POR_DIA_ATRASO = 2.00

    def __init__(self):
        self.emprestimos: List[Emprestimo] = []

    def solicitar_emprestimo(self, aluno: Aluno, livro: Livro,
                              hoje: Optional[date] = None) -> Optional[Emprestimo]:
        hoje = hoje or date.today()
        print(f"\n[1] {aluno.nome} solicita empréstimo do livro '{livro.titulo}'.")

        if len(aluno.emprestimos_ativos()) >= self.MAX_LIVROS_POR_ALUNO:
            print(f"[!] {aluno.nome} já possui {self.MAX_LIVROS_POR_ALUNO} "
                  f"livros emprestados. Empréstimo negado.")
            return None

        if not livro.disponivel():
            livro.fila_espera.append(aluno)
            print(f"[2A] Livro indisponível. {aluno.nome} entrou na fila de espera "
                  f"(posição {len(livro.fila_espera)}).")
            return None
        print("[2] Livro disponível.")

        if aluno.possui_multa():
            print(f"[3A] {aluno.nome} possui multa pendente de R$ "
                  f"{aluno.multas_pendentes:.2f}. Empréstimo bloqueado.")
            return None
        print("[3] Nenhuma pendência encontrada.")

        data_devolucao = hoje + timedelta(days=self.PRAZO_EMPRESTIMO_DIAS)
        emprestimo = Emprestimo(aluno=aluno, livro=livro,
                                 data_emprestimo=hoje,
                                 data_devolucao_prevista=data_devolucao)
        livro.copias_disponiveis -= 1
        aluno.emprestimos.append(emprestimo)
        self.emprestimos.append(emprestimo)
        print("[4] Empréstimo registrado.")
        print(f"[5] Data de devolução definida: {data_devolucao.strftime('%d/%m/%Y')}.")
        return emprestimo

    def devolver_livro(self, emprestimo: Emprestimo, data_devolucao: Optional[date] = None):
        data_devolucao = data_devolucao or date.today()
        emprestimo.status = "devolvido"
        emprestimo.livro.copias_disponiveis += 1

        if data_devolucao > emprestimo.data_devolucao_prevista:
            dias_atraso = (data_devolucao - emprestimo.data_devolucao_prevista).days
            multa = dias_atraso * self.MULTA_POR_DIA_ATRASO
            emprestimo.aluno.multas_pendentes += multa
            print(f"[!] Devolução com {dias_atraso} dia(s) de atraso. "
                  f"Multa aplicada: R$ {multa:.2f}.")
        else:
            print("[OK] Livro devolvido dentro do prazo.")

        if emprestimo.livro.fila_espera:
            proximo = emprestimo.livro.fila_espera.pop(0)
            print(f"[Fila] Notificando {proximo.nome}: livro "
                  f"'{emprestimo.livro.titulo}' disponível.")


def escolher_da_lista(itens: Dict[str, object], rotulo: str):
    if not itens:
        print(f"Nenhum(a) {rotulo} cadastrado(a) ainda.")
        return None
    chaves = list(itens.keys())
    for i, chave in enumerate(chaves, start=1):
        print(f"  {i}. {chave}")
    escolha = input(f"Escolha o número do(a) {rotulo}: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(chaves)):
        print("Escolha inválida.")
        return None
    return itens[chaves[int(escolha) - 1]]


def cadastrar_livro(livros: Dict[str, Livro]):
    titulo = input("Título do livro: ").strip()
    codigo = input("Código do livro: ").strip()
    try:
        copias = int(input("Quantidade de cópias disponíveis: "))
    except ValueError:
        copias = 1
    livros[codigo] = Livro(titulo=titulo, codigo=codigo, copias_disponiveis=copias)
    print(f"Livro '{titulo}' cadastrado.")


def cadastrar_aluno(alunos: Dict[str, Aluno]):
    nome = input("Nome do aluno: ").strip()
    matricula = input("Matrícula: ").strip()
    alunos[matricula] = Aluno(nome=nome, matricula=matricula)
    print(f"Aluno '{nome}' cadastrado.")


def solicitar_emprestimo_interativo(sistema: SistemaBiblioteca,
                                     alunos: Dict[str, Aluno],
                                     livros: Dict[str, Livro]):
    print("\nSelecione o aluno:")
    aluno = escolher_da_lista(alunos, "aluno")
    if aluno is None:
        return

    print("\nSelecione o livro:")
    livro = escolher_da_lista({l.codigo: l for l in livros.values()}, "livro")
    if livro is None:
        return

    sistema.solicitar_emprestimo(aluno, livro)


def devolver_livro_interativo(sistema: SistemaBiblioteca):
    ativos = [e for e in sistema.emprestimos if e.status == "ativo"]
    if not ativos:
        print("Nenhum empréstimo ativo.")
        return

    for i, e in enumerate(ativos, start=1):
        print(f"  {i}. {e.aluno.nome} - '{e.livro.titulo}' "
              f"(devolução prevista: {e.data_devolucao_prevista.strftime('%d/%m/%Y')})")
    escolha = input("Escolha o número do empréstimo a devolver: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(ativos)):
        print("Escolha inválida.")
        return

    emprestimo = ativos[int(escolha) - 1]
    texto_data = input("Data de devolução (dd/mm/aaaa) [Enter para hoje]: ").strip()
    if texto_data:
        try:
            data_devolucao = date(*[int(x) for x in reversed(texto_data.split("/"))])
        except ValueError:
            print("Data inválida, usando hoje.")
            data_devolucao = date.today()
    else:
        data_devolucao = date.today()

    sistema.devolver_livro(emprestimo, data_devolucao=data_devolucao)


def listar_emprestimos(sistema: SistemaBiblioteca):
    if not sistema.emprestimos:
        print("Nenhum empréstimo registrado.")
        return
    for e in sistema.emprestimos:
        print(f"- {e.aluno.nome} - '{e.livro.titulo}' [{e.status}] "
              f"devolução prevista {e.data_devolucao_prevista.strftime('%d/%m/%Y')}")


def menu():
    sistema = SistemaBiblioteca()
    alunos: Dict[str, Aluno] = {}
    livros: Dict[str, Livro] = {}

    opcoes = {
        "1": ("Cadastrar livro", lambda: cadastrar_livro(livros)),
        "2": ("Cadastrar aluno", lambda: cadastrar_aluno(alunos)),
        "3": ("Solicitar empréstimo", lambda: solicitar_emprestimo_interativo(sistema, alunos, livros)),
        "4": ("Devolver livro", lambda: devolver_livro_interativo(sistema)),
        "5": ("Listar empréstimos", lambda: listar_emprestimos(sistema)),
        "0": ("Sair", None),
    }

    while True:
        print("\n=== Sistema de Controle de Biblioteca Universitária ===")
        for chave, (texto, _) in opcoes.items():
            print(f"{chave}. {texto}")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando.")
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()


@dataclass
class Aluno:
    nome: str
    matricula: str
    emprestimos: List["Emprestimo"] = field(default_factory=list)
    multas_pendentes: float = 0.0

    def emprestimos_ativos(self) -> List["Emprestimo"]:
        return [e for e in self.emprestimos if e.status == "ativo"]

    def possui_multa(self) -> bool:
        return self.multas_pendentes > 0


@dataclass
class Emprestimo:
    aluno: Aluno
    livro: Livro
    data_emprestimo: date
    data_devolucao_prevista: date
    status: str = "ativo"


class SistemaBiblioteca:
    MAX_LIVROS_POR_ALUNO = 5
    PRAZO_EMPRESTIMO_DIAS = 14
    MULTA_POR_DIA_ATRASO = 2.00

    def __init__(self):
        self.emprestimos: List[Emprestimo] = []

    def solicitar_emprestimo(self, aluno: Aluno, livro: Livro,
                              hoje: Optional[date] = None) -> Optional[Emprestimo]:
        hoje = hoje or date.today()
        print(f"\n[1] {aluno.nome} solicita empréstimo do livro '{livro.titulo}'.")

        if len(aluno.emprestimos_ativos()) >= self.MAX_LIVROS_POR_ALUNO:
            print(f"[!] {aluno.nome} já possui {self.MAX_LIVROS_POR_ALUNO} "
                  f"livros emprestados. Empréstimo negado.")
            return None

        if not livro.disponivel():
            livro.fila_espera.append(aluno)
            print(f"[2A] Livro indisponível. {aluno.nome} entrou na fila de espera "
                  f"(posição {len(livro.fila_espera)}).")
            return None
        print("[2] Livro disponível.")

        if aluno.possui_multa():
            print(f"[3A] {aluno.nome} possui multa pendente de R$ "
                  f"{aluno.multas_pendentes:.2f}. Empréstimo bloqueado.")
            return None
        print("[3] Nenhuma pendência encontrada.")

        data_devolucao = hoje + timedelta(days=self.PRAZO_EMPRESTIMO_DIAS)
        emprestimo = Emprestimo(aluno=aluno, livro=livro,
                                 data_emprestimo=hoje,
                                 data_devolucao_prevista=data_devolucao)
        livro.copias_disponiveis -= 1
        aluno.emprestimos.append(emprestimo)
        self.emprestimos.append(emprestimo)
        print("[4] Empréstimo registrado.")
        print(f"[5] Data de devolução definida: {data_devolucao.strftime('%d/%m/%Y')}.")
        return emprestimo

    def devolver_livro(self, emprestimo: Emprestimo, data_devolucao: Optional[date] = None):
        data_devolucao = data_devolucao or date.today()
        emprestimo.status = "devolvido"
        emprestimo.livro.copias_disponiveis += 1

        if data_devolucao > emprestimo.data_devolucao_prevista:
            dias_atraso = (data_devolucao - emprestimo.data_devolucao_prevista).days
            multa = dias_atraso * self.MULTA_POR_DIA_ATRASO
            emprestimo.aluno.multas_pendentes += multa
            print(f"[!] Devolução com {dias_atraso} dia(s) de atraso. "
                  f"Multa aplicada: R$ {multa:.2f}.")
        else:
            print("[OK] Livro devolvido dentro do prazo.")

        if emprestimo.livro.fila_espera:
            proximo = emprestimo.livro.fila_espera.pop(0)
            print(f"[Fila] Notificando {proximo.nome}: livro "
                  f"'{emprestimo.livro.titulo}' disponível.")


def escolher_da_lista(itens: Dict[str, object], rotulo: str):
    if not itens:
        print(f"Nenhum(a) {rotulo} cadastrado(a) ainda.")
        return None
    chaves = list(itens.keys())
    for i, chave in enumerate(chaves, start=1):
        print(f"  {i}. {chave}")
    escolha = input(f"Escolha o número do(a) {rotulo}: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(chaves)):
        print("Escolha inválida.")
        return None
    return itens[chaves[int(escolha) - 1]]


def cadastrar_livro(livros: Dict[str, Livro]):
    titulo = input("Título do livro: ").strip()
    codigo = input("Código do livro: ").strip()
    try:
        copias = int(input("Quantidade de cópias disponíveis: "))
    except ValueError:
        copias = 1
    livros[codigo] = Livro(titulo=titulo, codigo=codigo, copias_disponiveis=copias)
    print(f"Livro '{titulo}' cadastrado.")


def cadastrar_aluno(alunos: Dict[str, Aluno]):
    nome = input("Nome do aluno: ").strip()
    matricula = input("Matrícula: ").strip()
    alunos[matricula] = Aluno(nome=nome, matricula=matricula)
    print(f"Aluno '{nome}' cadastrado.")


def solicitar_emprestimo_interativo(sistema: SistemaBiblioteca,
                                     alunos: Dict[str, Aluno],
                                     livros: Dict[str, Livro]):
    print("\nSelecione o aluno:")
    aluno = escolher_da_lista(alunos, "aluno")
    if aluno is None:
        return

    print("\nSelecione o livro:")
    livro = escolher_da_lista({l.codigo: l for l in livros.values()}, "livro")
    if livro is None:
        return

    sistema.solicitar_emprestimo(aluno, livro)


def devolver_livro_interativo(sistema: SistemaBiblioteca):
    ativos = [e for e in sistema.emprestimos if e.status == "ativo"]
    if not ativos:
        print("Nenhum empréstimo ativo.")
        return

    for i, e in enumerate(ativos, start=1):
        print(f"  {i}. {e.aluno.nome} - '{e.livro.titulo}' "
              f"(devolução prevista: {e.data_devolucao_prevista.strftime('%d/%m/%Y')})")
    escolha = input("Escolha o número do empréstimo a devolver: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(ativos)):
        print("Escolha inválida.")
        return

    emprestimo = ativos[int(escolha) - 1]
    texto_data = input("Data de devolução (dd/mm/aaaa) [Enter para hoje]: ").strip()
    if texto_data:
        try:
            data_devolucao = date(*[int(x) for x in reversed(texto_data.split("/"))])
        except ValueError:
            print("Data inválida, usando hoje.")
            data_devolucao = date.today()
    else:
        data_devolucao = date.today()

    sistema.devolver_livro(emprestimo, data_devolucao=data_devolucao)


def listar_emprestimos(sistema: SistemaBiblioteca):
    if not sistema.emprestimos:
        print("Nenhum empréstimo registrado.")
        return
    for e in sistema.emprestimos:
        print(f"- {e.aluno.nome} - '{e.livro.titulo}' [{e.status}] "
              f"devolução prevista {e.data_devolucao_prevista.strftime('%d/%m/%Y')}")


def menu():
    sistema = SistemaBiblioteca()
    alunos: Dict[str, Aluno] = {}
    livros: Dict[str, Livro] = {}

    opcoes = {
        "1": ("Cadastrar livro", lambda: cadastrar_livro(livros)),
        "2": ("Cadastrar aluno", lambda: cadastrar_aluno(alunos)),
        "3": ("Solicitar empréstimo", lambda: solicitar_emprestimo_interativo(sistema, alunos, livros)),
        "4": ("Devolver livro", lambda: devolver_livro_interativo(sistema)),
        "5": ("Listar empréstimos", lambda: listar_emprestimos(sistema)),
        "0": ("Sair", None),
    }

    while True:
        print("\n=== Sistema de Controle de Biblioteca Universitária ===")
        for chave, (texto, _) in opcoes.items():
            print(f"{chave}. {texto}")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando.")
            break
        if escolha in opcoes:
            opcoes[escolha][1]()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
