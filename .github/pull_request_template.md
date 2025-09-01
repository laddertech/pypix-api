# Pull Request

## 📝 Descrição

<!-- Descreva suas mudanças de forma clara e concisa -->

### Tipo de Mudança

<!-- Marque o tipo de mudança que melhor descreve seu PR -->

- [ ] 🐛 **Bug fix** - Corrige um bug existente
- [ ] ✨ **Feature** - Adiciona nova funcionalidade
- [ ] 💥 **Breaking change** - Mudança que quebra compatibilidade
- [ ] 📚 **Documentation** - Apenas mudanças na documentação
- [ ] 🧪 **Tests** - Adiciona ou modifica testes
- [ ] 🔧 **Refactor** - Refatoração sem mudanças funcionais
- [ ] 🏦 **Bank support** - Adiciona suporte a novo banco
- [ ] 🪝 **Webhook** - Funcionalidades relacionadas a webhooks
- [ ] 🔄 **Recurring** - Funcionalidades de pagamentos recorrentes
- [ ] ⚡ **Performance** - Melhorias de performance
- [ ] 🔒 **Security** - Correções de segurança
- [ ] 🛠️ **Chore** - Manutenção, CI/CD, build, etc.

### Banco Afetado (se aplicável)

- [ ] Banco do Brasil
- [ ] Sicoob
- [ ] Ambos
- [ ] N/A - Mudança geral

## 🔗 Issue Relacionada

<!-- Link para a issue que este PR resolve, se aplicável -->
Fixes #(número da issue)

## 📋 Mudanças Detalhadas

<!-- Liste as principais mudanças realizadas -->

- [ ] Mudança 1
- [ ] Mudança 2
- [ ] Mudança 3

## 🧪 Como Testar

<!-- Descreva os passos para testar suas mudanças -->

### Pré-requisitos
<!-- Liste o que é necessário para testar -->

- [ ] Credenciais de sandbox configuradas
- [ ] Certificados de teste
- [ ] Outro:

### Passos para Testar

1. Configure o ambiente:
   ```bash
   # Passos de configuração
   ```

2. Execute os testes:
   ```bash
   make test
   # ou comandos específicos
   ```

3. Teste manual (se aplicável):
   ```python
   # Exemplo de código para testar manualmente
   ```

4. Verifique que:
   - [ ] Testes automatizados passam
   - [ ] Funcionalidade funciona conforme esperado
   - [ ] Não quebra funcionalidades existentes

## 📊 Cobertura de Testes

<!-- Informações sobre testes adicionados ou modificados -->

- [ ] Testes unitários adicionados/atualizados
- [ ] Testes de integração adicionados/atualizados
- [ ] Cobertura de testes mantida ou melhorada
- [ ] N/A - Não requer testes

**Cobertura atual:** <!-- Se disponível, adicione o percentual -->

## 📚 Documentação

<!-- Marque todas as opções que se aplicam -->

- [ ] README atualizado
- [ ] CHANGELOG.md atualizado
- [ ] Documentação da API atualizada (docstrings)
- [ ] Exemplos de uso adicionados/atualizados
- [ ] Documentação Sphinx atualizada
- [ ] N/A - Não requer documentação

## ⚡ Performance

<!-- Se aplicável, informações sobre impacto na performance -->

- [ ] Esta mudança melhora a performance
- [ ] Esta mudança não afeta a performance
- [ ] Esta mudança pode impactar a performance (explicar abaixo)
- [ ] N/A

**Detalhes de performance:** <!-- Se relevante -->

## 🔒 Considerações de Segurança

<!-- Marque se aplicável -->

- [ ] Esta mudança não introduz vulnerabilidades de segurança
- [ ] Esta mudança melhora a segurança
- [ ] Esta mudança pode ter impactos de segurança (explicar abaixo)
- [ ] Revisão de segurança necessária

**Detalhes de segurança:** <!-- Se relevante -->

## ✅ Checklist do Desenvolvedor

<!-- Marque todos os itens antes de submeter o PR -->

### Código
- [ ] Meu código segue as convenções de estilo do projeto
- [ ] Realizei self-review do meu código
- [ ] Comentei partes complexas do código
- [ ] Removi código comentado ou de debug desnecessário
- [ ] Não há informações sensíveis no código (tokens, senhas, etc.)

### Testes
- [ ] Adicionei testes que provam que minha correção é efetiva ou que minha funcionalidade funciona
- [ ] Testes unitários existentes passam localmente
- [ ] Testes de integração passam (se aplicável)

### Documentação
- [ ] Atualizei documentação relevante
- [ ] Docstrings estão completas e seguem o padrão Google
- [ ] Exemplos de uso estão atualizados

### Git & CI
- [ ] Commits seguem o padrão Conventional Commits
- [ ] Branch está atualizada com a main/develop
- [ ] CI/CD passa sem erros
- [ ] Pre-commit hooks foram executados

### Compatibilidade
- [ ] Mudanças são backwards compatible
- [ ] Se breaking change, está documentado e justificado
- [ ] Testado em Python 3.10, 3.11, 3.12 (ou CI confirma)

## 🔄 Migration Guide

<!-- Se este é um breaking change, forneça um guia de migração -->

<!--
### Para usuários que usam versão X.X.X:

```python
# Antes
old_way = api.old_method()

# Agora
new_way = api.new_method()
```
-->

## 📸 Screenshots

<!-- Se aplicável, adicione screenshots ou logs que demonstram a funcionalidade -->

## 🤝 Revisão

<!-- Informações para os revisores -->

### Areas de Foco para Revisão

<!-- Destaque areas específicas onde você gostaria de feedback -->

- [ ] Lógica de negócio
- [ ] Tratamento de erros
- [ ] Performance
- [ ] Segurança
- [ ] Documentação
- [ ] Testes

### Perguntas para Revisores

<!-- Faça perguntas específicas se tiver dúvidas -->

## 📞 Contato

Se você tiver perguntas sobre este PR, me mencione (@seu-usuario) ou entre em contato em fabio@ladder.dev.br

---

**Obrigado por contribuir com o pypix-api! 🚀**
