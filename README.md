# Tinder Jobs - Visão Geral do Projeto

## Descrição do Projeto

Tinder Jobs é uma aplicação web projetada para conectar desenvolvedores a oportunidades de emprego de forma simples e interativa. O projeto é inspirado na interface de "swipe" do Tinder, permitindo que desenvolvedores e empresas façam "matches" com base em suas preferências e necessidades.

Este projeto permite:
- Desenvolvedores navegarem e se candidatarem a vagas de emprego.
- Empresas postarem vagas e gerenciarem candidatos.
- Tanto desenvolvedores quanto empresas visualizarem e gerenciarem seus "matches", candidaturas e entrevistas.

## Funcionalidades

- Autenticação de usuários para desenvolvedores e empresas.
- Perfis para desenvolvedores, incluindo habilidades, preferências e histórico de candidaturas.
- Empresas podem criar e gerenciar vagas de emprego.
- Funcionalidade de "match" entre desenvolvedores e vagas de emprego.
- Painel de controle para gerenciar candidaturas e ofertas de emprego.
- Upload seguro de arquivos para imagens de perfil e outros conteúdos.

## Tecnologias Utilizadas

- **Flask**: Framework web para construção da aplicação.
- **Bootstrap Flask**: Integração do Bootstrap para estilizar o frontend.
- **WTForms**: Para lidar com formulários e validação.
- **Flask-WTF**: Integração do WTForms com o Flask.
- **SQLAlchemy**: ORM para gerenciamento do banco de dados.
- **Werkzeug**: Utilitários para uploads de arquivos e segurança.

## Estrutura do Projeto

```
projeto-tinder/
│
├── instance/
│   └── devs.db                   # Banco de dados SQLite
├── static/
│   ├── css/
│   │   └── styles.css             # Estilos para o frontend
│   ├── images/                    # Ícones e logotipo usados no projeto
│   └── uploads/                   # Imagens enviadas
├── templates/                     # Templates HTML para diferentes páginas
│   └── *.html
├── devs-data.csv                  # Dados em CSV dos desenvolvedores
├── main.py                        # Lógica principal da aplicação
├── requirements.txt               # Dependências do projeto
├── README.md                      # Arquivo README do projeto
└── ...
```

## Instruções de Configuração

Para configurar e rodar o projeto localmente, siga os passos abaixo:

### Pré-requisitos
Certifique-se de ter os seguintes itens instalados:
- Python 3.x
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório:**

   ```bash
   git clone <repository-url>
   cd projeto-tinder
   ```

2. **Crie um ambiente virtual:**

   No Windows:
   ```bash
   py -3 -m venv .venv
   .venv\Scripts\activate
   ```

   No macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Execute a aplicação:**

   ```bash
   python main.py
   ```

5. **Acesse a aplicação:**
   Abra o navegador e vá para `http://127.0.0.1:5000/`

## Banco de Dados

O projeto utiliza SQLite como banco de dados. Um banco de dados pré-configurado (`devs.db`) é fornecido, mas você pode substituí-lo ou migrar a estrutura se necessário.

## Contribuindo

Sinta-se à vontade para fazer um fork do repositório e enviar pull requests caso deseje contribuir com o projeto.
