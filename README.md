# Hotel Tung Tung

Sistema de gerenciamento de reservas para um hotel, desenvolvido como projeto semestral da disciplina **Programação com Acesso a Banco de Dados (PABD)**.

## Funcionalidades

- **Autenticação** — Login seguro com senha hash (SHA-256) e controle de acesso por cargo (admin/atendente).
- **Dashboard** — Cards com KPIs (reservas hoje, quartos ocupados, pendentes, faturamento do mês) e tabelas de últimas reservas e próximos check-ins.
- **Clientes** — Cadastro completo (CRUD) com validação de CPF.
- **Quartos** — Cadastro completo (CRUD) com campos de descrição e tipo (solteiro/casal/suite); busca de disponibilidade por período.
- **Reservas** — Cadastro com seleção de cliente/quarto, filtros por data/status/cliente, e fluxo de status (pendente → confirmada → finalizada; cancelamento a qualquer momento).
- **Usuários** — Gerenciamento de acesso ao sistema (admin apenas).

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.13 |
| Interface | Tkinter + ttkbootstrap (tema *flatly*) |
| ORM | SQLAlchemy 2.0 |
| Banco | MySQL 8.0 (Docker) |
| Migrações | Alembic |
| Container | Docker Compose |

## Estrutura do Projeto

```
pabd/
├── src/
│   ├── main.py             
│   ├── apresentacao/       
│   ├── negocio/            
│   ├── dados/              
│   ├── dominio/            
│   └── comandos/           
├── migrations/versions/    
├── db/init.sql             
├── docker-compose.yml      
├── requirements.txt
└── .env.example
```

## Como Executar

```bash
# 1. Iniciar o banco
docker compose up -d

# 2. Ativar ambiente virtual
source .venv/bin/activate

# 3. Rodar a aplicação
python3 src/main.py
```

## O que ainda pode ser implementado

- Exportação de relatórios (PDF/CSV)
- Busca/filtro nas telas de Clientes e Usuários
- Manutenção/indisponibilidade de quartos
- Processo de check-in / check-out distinto
- Configuração de descontos e taxas
- Validação de dígitos verificadores do CPF
