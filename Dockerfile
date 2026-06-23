# Imagem base leve do Python 3
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o script do sistema de gerenciamento de alunos para o contêiner
COPY sistema_alunos.py .

# Comando padrão ao iniciar o contêiner: executa o sistema de forma interativa
CMD ["python", "sistema_alunos.py"]
