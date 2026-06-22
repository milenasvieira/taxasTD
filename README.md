📈 Monitor de Taxas do Tesouro Direto Script em Python que monitora as taxas dos títulos do Tesouro Direto e envia alertas via Telegram quando há aumento significativo. Ideal para investidores que querem ser avisados em tempo real sobre oportunidades de compra.

📋 Funcionalidades ✅ Obtém taxas de compra e venda de títulos do Tesouro Direto

✅ Compara com a taxa anterior e dispara alerta se houver aumento

✅ Envia mensagens com formatação **HTML** via Telegram

✅ Modo mock para testes sem dados reais

✅ Suporte a múltiplos títulos (lista configurável)

✅ Deploy fácil no Render (gratuito) com agendador externo

✅ Arquivo .env para configuração segura

✅ Estado persistente em **JSON** para evitar alertas duplicados

🛠️ Tecnologias Python 3.9+

Flask (para servir como Web Service)

Requests (para consumo de APIs)

python-dotenv (gerenciamento de variáveis de ambiente)

Telegram Bot **API** (envio de alertas)

Render (deploy gratuito) + cron-job.org (agendador)

🔐 Pré-requisitos Conta no Telegram e um bot criado via @BotFather

Python 3.9+ instalado localmente (para testes)

(Opcional) Conta no Render para deploy

(Opcional) Conta no cron-job.org para agendamento

⚙️ Configuração local ## Clone o repositório bash git clone [https://github.com/seu-usuario/monitor-tesouro.git](https://github.com/seu-usuario/monitor-tesouro.git) cd monitor-tesouro ## Crie um ambiente virtual (recomendado) bash python -m venv venv source venv/bin/activate      # Linux/Mac # ou venv\Scripts\activate         # Windows ## Instale as dependências bash pip install -r requirements.txt ## Configure o arquivo .env Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

env # Tokens do Telegram (obtidos no @BotFather) TELEGRAM_TOKEN=seu_token_aqui TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Modo de execução: True = dados mockados, False = API real (brapi.dev Pro)

MOCK_MODE=True

# Intervalo entre verificações (em segundos) - usado apenas localmente

CHECK_INTERVAL=30

# Símbolos dos títulos (separados por vírgula)

**SYMBOLS**=tesouro-selic-**01032031**,tesouro-prefixado-com-juros-semestrais-**01012037**,tesouro-ipca-com-juros-semestrais-**15082060** ## Como obter seu TELEGRAM_CHAT_ID Envie uma mensagem para seu bot no Telegram.

Acesse a **URL** no navegador:

text [https://api.telegram.org/botSEU_TOKEN/getUpdates](https://api.telegram.org/botSEU_TOKEN/getUpdates) O chat_id aparecerá no **JSON** retornado.

Alternativa: use o bot @userinfobot que retorna seu ID diretamente.

▶️ Execução local Com loop infinito (monitor contínuo) bash python monitor_tesouro.py O script verificará as taxas a cada CHECK_INTERVAL segundos e enviará alertas quando houver aumento.

Como Web Service (para deploy) bash python index.py Acesse [http://localhost:**5000**/check-rates](http://localhost:**5000**/check-rates) para executar uma verificação manual.

☁️ Deploy no Render (gratuito) ## Faça o push do código para um repositório GitHub Certifique-se de que os arquivos index.py, requirements.txt, .env.example (opcional) e .gitignore estejam na raiz.

## Crie um Web Service no Render

Acesse render.com e crie uma conta.

Clique em New + > Web Service.

Conecte seu repositório GitHub.

Preencha:

Name: monitor-tesouro

Environment: Python 3

Build Command: pip install -r requirements.txt

Start Command: gunicorn index:app

Plan: Free

## Configure as variáveis de ambiente

No painel do seu serviço no Render, vá em Environment > Add Environment Variable e adicione:

Chave	Valor
TELEGRAM_TOKEN	token do seu bot
TELEGRAM_CHAT_ID	seu chat_id
MOCK_MODE	True ou False
**SYMBOLS**	lista de símbolos separados por vírgula (opcional)
## Aguarde o build e obtenha a URL do serviço
Exemplo: [https://monitor-tesouro.onrender.com](https://monitor-tesouro.onrender.com)

⏰ Configurar o agendador externo (cron-job.org) Como o plano gratuito do Render *dorme* após 15 minutos, usamos um agendador externo para manter o serviço ativo e executar a verificação periodicamente.

## Crie uma conta em cron-job.org

## Crie um novo *Cron Job* Title: Monitor Tesouro

**URL**: [https://seu-app.onrender.com/check-rates](https://seu-app.onrender.com/check-rates)

Cron Expression: */5 * * * * (a cada 5 minutos)

Method: **GET**

3. Salve
A partir de agora, seu serviço será *acordado* a cada 5 minutos e executará a verificação automaticamente.

📁 Estrutura de arquivos
text
monitor-tesouro/
├── index.py                # Aplicação Flask (para deploy)
├── monitor_tesouro.py      # Script com loop infinito (execução local)
├── requirements.txt        # Dependências do projeto
├── .env                    # Configurações (NÃO commitado)
├── .env.example            # Modelo do .env (commitado)
├── .gitignore              # Arquivos ignorados pelo Git
├── **README**.md               # Este arquivo
└── last_rates.json         # Estado anterior (gerado automaticamente)
🧪 Modo Mock vs. Modo Real
Modo	Variável MOCK_MODE	Fonte de dados	Uso
Mock	True	Dados fictícios com variação aleatória	Testes sem internet e sem **API**
Real	False	**API** da brapi.dev (requer plano Pro)	Produção com dados reais
🔔 Exemplo de Alerta no Telegram
text
🚨 **AUMENTO** **NAS** **TAXAS**!

📈 Tesouro Selic **2031** Taxa: 13.**6500**% (antes 13.**5500**%) Aumento: 0.**1000** p.p. Venc: 01/03/**2031** | Preço: R$ **987**.50 📦 Dependências principais txt Flask==2.3.3 requests==2.31.0 python-dotenv==1.0.0 gunicorn==21.2.0