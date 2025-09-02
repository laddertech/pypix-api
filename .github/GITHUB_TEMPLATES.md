# GitHub Templates e Automação

Este diretório contém templates e configurações de automação para melhorar a experiência de contribuição e manutenção do projeto pypix-api.

## 📝 Templates de Issues

Localizados em `.github/ISSUE_TEMPLATE/`:

### 🐛 Bug Report (`bug_report.yml`)
Para reportar bugs e problemas encontrados no pypix-api.
- Coleta informações sobre reprodução
- Identifica banco específico afetado
- Captura detalhes do ambiente (Python, OS)
- Solicita logs e contexto adicional

### ✨ Feature Request (`feature_request.yml`)
Para sugerir novas funcionalidades e melhorias.
- Categoriza por tipo de funcionalidade
- Define prioridade e caso de uso
- Solicita exemplos de API desejada
- Coleta referências e documentação relevante

### 🏦 Bank Support (`bank_support.yml`)
Específico para solicitar suporte a novos bancos.
- Identifica urgência do suporte
- Coleta informações da API do banco
- Oferece formas de colaboração
- Captura documentação técnica disponível

### 📚 Documentation (`documentation.yml`)
Para problemas e sugestões na documentação.
- Identifica localização específica do problema
- Categoriza tipo de melhoria necessária
- Define audiência alvo
- Solicita exemplos e contexto de uso

### ❓ Question (`question.yml`)
Para perguntas gerais sobre uso do pypix-api.
- Categoriza por área (configuração, autenticação, etc.)
- Coleta contexto sobre o caso de uso
- Identifica banco específico (se aplicável)
- Captura tentativas anteriores de solução

### ⚙️ Configuração (`config.yml`)
- Desabilita issues em branco
- Define links de contato alternativos:
  - GitHub Discussions para discussões gerais
  - Documentação para consulta
  - Email para questões comerciais
  - Security tab para vulnerabilidades

## 🔄 Template de Pull Request

Localizado em `.github/pull_request_template.md`:

### Estrutura Completa
- **Tipo de mudança**: Categorização clara (bug, feature, etc.)
- **Banco afetado**: Identificação de impacto específico
- **Como testar**: Passos detalhados para validação
- **Cobertura de testes**: Informações sobre testes adicionados
- **Documentação**: Checklist de documentação atualizada
- **Considerações**: Performance, segurança, breaking changes
- **Checklist**: Validação completa antes do merge

### Categorias Suportadas
- 🐛 Bug fix
- ✨ Feature
- 💥 Breaking change
- 📚 Documentation
- 🧪 Tests
- 🔧 Refactor
- 🏦 Bank support
- 🪝 Webhook
- 🔄 Recurring
- ⚡ Performance
- 🔒 Security
- 🛠️ Chore

## 🤖 Dependabot

Configurado em `.github/dependabot.yml`:

### Python Dependencies
- **Frequência**: Semanal (segunda-feira às 6h, horário de Brasília)
- **Agrupamento**: Por categoria (produção, desenvolvimento, documentação)
- **Limite**: 5 PRs abertos por vez
- **Ignore**: Major updates para dependências críticas (requests, python-dotenv)

### GitHub Actions
- **Frequência**: Semanal (segunda-feira às 6h30, horário de Brasília)
- **Agrupamento**: Todas as actions juntas
- **Limite**: 3 PRs abertos por vez

### Configurações Gerais
- **Reviewers/Assignees**: fabio-thomaz
- **Labels**: Automáticas por categoria
- **Commit message**: Seguem padrão conventional commits

## 🔄 Workflows Adicionais

### Dependency Review (`.github/workflows/dependency-review.yml`)
- **Trigger**: PRs que modificam dependências
- **Função**: Analisa vulnerabilidades e licenças
- **Configuração**:
  - Falha em vulnerabilidades moderate+
  - Permite licenças comuns (MIT, Apache, BSD, etc.)
  - Comenta resultados no PR

### Auto-merge Dependabot (`.github/workflows/auto-merge-dependabot.yml`)
- **Trigger**: PRs do Dependabot
- **Função**: Merge automático de updates patch/minor
- **Configuração**:
  - Aguarda CI passar (timeout: 30 min)
  - Auto-aprova updates menores
  - Requer review manual para major updates
  - Adiciona comentários explicativos

### Stale Management (`.github/workflows/stale.yml`)
- **Frequência**: Diária às 8h UTC (5h horário de Brasília)
- **Issues**: 60 dias para marcar stale, 14 dias para fechar
- **PRs**: 30 dias para marcar stale, 7 dias para fechar
- **Exceções**: Labels específicas (pinned, security, etc.)
- **Configuração**: Mensagens personalizadas em português

## 🎯 Benefícios

### Para Contribuidores
- **Orientação clara**: Templates guiam na criação de issues/PRs qualitativas
- **Padronização**: Todos seguem a mesma estrutura
- **Eficiência**: Menos ida e volta para esclarecimentos
- **Categorização**: Facilita identificar tipo de contribuição

### Para Mantenedores
- **Triagem**: Informações consistentes facilitam análise
- **Automação**: Dependabot e workflows reduzem trabalho manual
- **Qualidade**: Templates forçam qualidade mínima de informação
- **Organização**: Labels e categorias automáticas

### Para o Projeto
- **Profissionalismo**: Aparência polida e organizada
- **Escalabilidade**: Processos que funcionam com mais contribuidores
- **Manutenção**: Updates automáticos mantêm dependências atualizadas
- **Segurança**: Review automático de vulnerabilidades

## 🚀 Próximos Passos

1. **Monitorar efetividade** dos templates nos próximos PRs/issues
2. **Ajustar workflows** baseado no feedback da comunidade
3. **Adicionar mais automações** conforme necessário
4. **Documentar processos** para novos mantenedores

## 📞 Suporte

Para questões sobre templates e automações:
- Issues: Use os próprios templates para reportar problemas
- Email: fabio@ladder.dev.br
- Discussions: Para sugestões e melhorias
