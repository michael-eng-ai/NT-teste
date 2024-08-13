graph TD
    A[Fonte de Dados: CSV público] -->|Extração| B[Python Script]
    B -->|Transformação| C[Dados Limpos e Transformados]
    C -->|Carregamento| D[Databricks]
    D --> E[Delta Lake]
    E -->|Análise| F[Jupyter Notebooks]
    F -->|Visualização| G[Dashboards]
    H[Monitoramento] -->|Logs e Métricas| B
    H -->|Logs e Métricas| D
    I[Segurança] -->|Criptografia e Controle de Acesso| B
    I -->|Criptografia e Controle de Acesso| D
    I -->|Criptografia e Controle de Acesso| E