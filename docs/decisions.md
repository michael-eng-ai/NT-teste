# Decisões Técnicas e Arquiteturais do Projeto COVID-19 ETL e Análise

Este documento detalha as principais decisões tomadas durante o desenvolvimento do projeto, explicando o raciocínio por trás de cada escolha.

## 1. Framework de Processamento: Dask

**Decisão:** Utilizamos Dask como principal framework de processamento de dados.

**Motivo:** 
- Dask oferece processamento paralelo e distribuído, similar ao Spark, mas com uma integração mais suave com o ecossistema Python.
- Permite escalar facilmente de um laptop para um cluster.
- Mantém uma API familiar para usuários de Pandas, facilitando a transição e reduzindo a curva de aprendizado.

**Alternativas Consideradas:**
- Apache Spark: Mais robusto para clusters muito grandes, mas com uma curva de aprendizado mais íngreme.
- Pandas: Excelente para datasets menores, mas limitado em termos de escalabilidade.

## 2. Formato de Armazenamento: Parquet com PyArrow

**Decisão:** Escolhemos armazenar os dados processados em formato Parquet, utilizando PyArrow para leitura/escrita.

**Motivo:**
- Parquet é um formato colunar que oferece compressão eficiente e leitura rápida.
- PyArrow proporciona operações de I/O extremamente rápidas.
- Boa integração com várias ferramentas de análise de dados, incluindo Dask e Spark.

**Alternativas Consideradas:**
- CSV: Simples, mas ineficiente para grandes volumes de dados.
- Apache Avro: Bom para dados com esquemas que evoluem, mas menos eficiente para análises colunares.

## 3. Análise e Visualização: Matplotlib e Seaborn

**Decisão:** Utilizamos Matplotlib e Seaborn para análises e visualizações.

**Motivo:**
- Matplotlib é versátil e bem estabelecido no ecossistema Python.
- Seaborn oferece uma interface de alto nível para criação de visualizações estatísticas atraentes.
- Ambas as bibliotecas são bem documentadas e têm amplo suporte da comunidade.

**Alternativas Consideradas:**
- Plotly: Oferece gráficos interativos, mas requer mais configuração para uso offline.
- Bokeh: Bom para dashboards interativos, mas com uma curva de aprendizado mais íngreme.

## 4. Segurança: Criptografia com Fernet

**Decisão:** Implementamos criptografia de arquivos usando a biblioteca Fernet.

**Motivo:**
- Fernet fornece criptografia simétrica fácil de usar e segura.
- Parte da biblioteca `cryptography`, que é bem mantida e auditada para segurança.
- Oferece um bom equilíbrio entre segurança e facilidade de implementação.

**Alternativas Consideradas:**
- PyCryptodome: Mais baixo nível, oferecendo mais controle, mas requerendo mais conhecimento criptográfico.
- Homemade Encryption: Descartada devido aos riscos de segurança associados à implementação própria de criptografia.

## 5. Logging e Monitoramento: Biblioteca padrão logging e psutil

**Decisão:** Utilizamos a biblioteca padrão `logging` do Python para logs e `psutil` para monitoramento de recursos.

**Motivo:**
- `logging` é uma solução robusta e flexível que não requer dependências externas.
- `psutil` oferece uma maneira multiplataforma de monitorar o uso de recursos do sistema.
- Ambas são bem documentadas e fáceis de integrar.

**Alternativas Consideradas:**
- ELK Stack (Elasticsearch, Logstash, Kibana): Mais poderoso, mas excessivo para as necessidades atuais do projeto.
- Prometheus + Grafana: Excelente para monitoramento em tempo real, mas requer infraestrutura adicional.

## 6. Ambiente de Desenvolvimento: Local com Potencial para Databricks

**Decisão:** Desenvolvemos inicialmente em um ambiente local, mas com a arquitetura preparada para migração futura para Databricks.

**Motivo:**
- Desenvolvimento local permite iterações rápidas e facilita o debugging.
- A estrutura do código (separação de ETL e análise) facilita a migração para Databricks no futuro.
- Databricks oferece escalabilidade e integração com Delta Lake, que pode ser benéfico conforme o projeto cresce.

**Alternativas Consideradas:**
- Desenvolvimento direto no Databricks: Mais próximo do ambiente de produção, mas potencialmente mais lento para iterações iniciais.
- Uso de serviços cloud nativos (ex: AWS EMR): Oferece mais controle, mas requer mais configuração e manutenção.

## Conclusão

Estas decisões foram tomadas considerando o equilíbrio entre performance, facilidade de uso, segurança e escalabilidade futura. Estamos abertos a reavaliar estas escolhas conforme o projeto evolui e novos requisitos surgem.