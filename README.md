# Sistema de Gerenciamento de Cinema

Projeto web desenvolvido com **Django** e banco de dados **PostgreSQL** (hospedado na plataforma [Neon](https://neon.tech)), com funcionalidades completas para gerenciamento de **usuários**, **reservas** de assentos e **emissão de bilhetes**. Inclui também uma interface de dashboard para administradores.


## Funcionalidades Principais

- Autenticação e registro de usuários (com token)
- Diferenciação entre usuários comuns e administradores
- CRUD completo de reservas
- Painel administrativo para gestão de reservas e usuários
- API RESTful documentada
- Suporte a filtros, atualização de status e estatísticas de reservas
- Conexão segura com banco PostgreSQL remoto via Neon


## 🛠️ Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/)
- [Django 4.x](https://www.djangoproject.com/)
- [PostgreSQL](https://www.postgresql.org/) (via [Neon](https://neon.tech))
- [Django REST Framework](https://www.django-rest-framework.org/)
- Token Authentication
- HTML/CSS para o painel 



## 🧪 Instalação Local (Desenvolvimento)

1. **Clone o projeto**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
````

2. **Crie um ambiente virtual e ative**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente**

Crie um arquivo `.env` na raiz com os dados da sua base Neon:

```env
DB_NAME=cinemabd
DB_USER=cinemabd_owner
DB_PASSWORD=sua_senha
DB_HOST=ep-endereco-do-neon.neon.tech
DB_PORT=5432
```

5. **Aplique as migrações e rode o servidor**

```bash
python manage.py migrate
python manage.py runserver
```

---

## Autenticação

A API utiliza **Token Authentication**. Após o login, inclua o token no cabeçalho de todas as requisições autenticadas:

```
Authorization: Token seu_token_aqui
```

---

## Endpoints da API

Alguns endpoints disponíveis:

| Método | Endpoint                             | Descrição                     |
| ------ | ------------------------------------ | ----------------------------- |
| POST   | /api/usuarios/registro/              | Registro de usuário           |
| POST   | /api/usuarios/login/                 | Login e obtenção de token     |
| GET    | /api/usuarios/meu-perfil/            | Ver perfil do usuário         |
| POST   | /api/reservas/reservas/              | Criar nova reserva            |
| GET    | /api/reservas/reservas/              | Listar reservas do usuário    |
| PATCH  | /api/reservas/{id}/update\_status/   | Atualizar status da reserva   |
| GET    | /api/reservas/reservas/estatisticas/ | Ver estatísticas das reservas |



## Dashboard Admin

O sistema possui uma interface de dashboard para administração de usuários e reservas, acessível para usuários com permissão de administrador.



## Permissões

* **Usuário comum**: pode registrar-se, autenticar, gerenciar seu perfil e suas reservas.
* **Administrador**: acesso completo a todos os dados, estatísticas e funcionalidades do painel.

---

## Notas Finais

* Tokens não expiram automaticamente, mas podem ser revogados via logout.
* O sistema segue boas práticas RESTful e validações de entrada.
* O projeto está em constante evolução. Contribuições são bem-vindas!


## Versão

* **v1.0**
* Última atualização: **Junho de 2025**



## Licença

Este projeto está sob a licença [MIT](LICENSE).


---

Se quiser, posso também gerar o arquivo `.env.example`, o `requirements.txt` e a estrutura mínima do repositório para deixar seu projeto pronto para ser clonado e usado facilmente. Deseja isso?
