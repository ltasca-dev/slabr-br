# TEMPLATE DE CONTATO: Bynx.gg Partnership

**Use este template para iniciar conversas com o time de bynx.gg**

---

## EMAIL TEMPLATE 1: Primeira Abordagem (Formal)

```
Assunto: Partnership Proposal - SLABR + Bynx.gg Integration

Olá team Bynx,

Meu nome é [NOME] e sou [CARGO] da SLABR, uma plataforma brasileira 
de gerenciamento de coleções de trading cards.

Temos grande admiração pelo trabalho que vocês estão fazendo em bynx.gg, 
especialmente na:
- Estrutura de database de cartas Pokémon TCG
- Sistema de rastreamento de preços em Real
- Comunidade de colecionadores brasileiros

Somos gestores de coleções TCG e estamos explorando oportunidades de 
parceria estratégica que possam beneficiar ambas as comunidades.

Gostaríamos de conversar sobre:
1. Possível integração de dados de preços
2. Compartilhamento de APIs
3. Integração de marketplaces
4. Colaboração comunitária

Vocês teriam interesse em uma reunião de 30 minutos para explorar 
essas oportunidades?

Melhor forma de entrar em contato: [EMAIL] ou [TELEFONE]

Obrigado,
[NOME]
SLABR Team
```

---

## EMAIL TEMPLATE 2: Seguimento (Mais Específico)

```
Assunto: SLABR Integration Proposal - Technical Details

Olá [CONTACT NAME],

Seguindo nossa conversa anterior, gostaria de compartilhar mais detalhes 
sobre como imaginamos a parceria:

BENEFÍCIOS MÚTUOS:

Para Bynx:
- Acesso ao userbase SLABR (crescimento de 20-50%)
- Co-marketing para comunidade brasileira de TCG
- Validação de features antes de launch
- Revenue share em transações marketplace

Para SLABR:
- Database de cartas Pokémon TCG brasileiras
- Preços em tempo real (market intelligence)
- Integração com comunidade bynx.gg
- Dados históricos de preços

MODELO DE INTEGRAÇÃO (Fase 1):
- API simples de preços de cartas
- Webhook para notificações de mudanças
- OAuth para sincronização de coleções
- Compartilhamento de listings de marketplace

TIMELINE:
- Semana 1: Discussão de termos
- Semana 2-4: Documentação de API
- Semana 5-8: Implementação
- Semana 9: Teste beta
- Semana 10: Launch

PRÓXIMOS PASSOS:
1. Confirmam interesse em discussão mais profunda?
2. Podem compartilhar documentação técnica de API?
3. Há um lead técnico que possa participar de reunião?

Fico no aguardo.

Abraços,
[NOME]
SLABR Team
```

---

## EMAIL TEMPLATE 3: Para Tech Lead (Técnico)

```
Assunto: Technical Integration Discussion - API Specification

Olá [TECH LEAD NAME],

Espero que esteja bem. Somos a SLABR e gostaria de discutir uma possível 
integração técnica com bynx.gg.

Estou compartilhando uma proposta de integração que preparamos:

ENDPOINTS NECESSÁRIOS:

1. GET /api/v1/cards/{card_id}
   - Retorna dados da carta (nome, edição, imagens, variantes)
   - Cache: 30-60 minutos
   - Rate limit: 100 req/min

2. GET /api/v1/cards/{card_id}/prices
   - Retorna preços atuais em R$
   - Cache: 10 minutos
   - Rate limit: 200 req/min

3. GET /api/v1/cards/search?q={query}
   - Busca de cartas
   - Cache: 60 minutos
   - Rate limit: 100 req/min

4. GET /api/v1/sets
   - Lista de edições disponíveis
   - Cache: 24 horas
   - Rate limit: 10 req/min

AUTENTICAÇÃO:
- OAuth 2.0 com access_token + refresh_token
- Client credentials flow para API calls
- Webhook signatures com HMAC-SHA256

WEBHOOKS (Optional):
- price_changed: Quando preço de carta muda >5%
- set_released: Quando nova edição é lançada
- card_added: Quando nova carta é adicionada

SEGURANÇA:
- Rate limiting por endpoint
- IP whitelist (de nossa infra)
- HTTPS obrigatório
- Versionamento de API

DADOS QUE PRECISAMOS:
- Card ID mapping (nosso formato vs bynx formato)
- Images (small: 100x140px, large: 300x420px)
- Price history (últimos 90 dias)
- Inventory data (se possível)

Vocês estão alinhados com essa arquitetura?

Fico aberto a discussão de detalhes.

Abraços,
[NOME] - Technical Lead, SLABR
```

---

## EMAIL TEMPLATE 4: Para Business Development

```
Assunto: Strategic Partnership - Revenue Sharing Model

Olá [BD NAME],

Como VP de Business Development da SLABR, gostaria de explorar uma 
partnership estratégica com bynx.gg que beneficie ambas as empresas.

VISÃO:

Integrar bynx.gg como a fonte de dados de preços oficial para SLABR, 
tornando-nos o ecossistema brasileiro completo de TCG.

PROPOSTA FINANCEIRA:

Cenário A (Conservative):
- Bynx recebe: 2-3% de cada transação marketplace em SLABR
- SLABR recebe: Acesso à API de preços
- Prazo: 12 meses
- Valor estimado: R$ 50-100K ano 1

Cenário B (Growth):
- Revenue share 50-50 em novas features conjuntas
- Co-marketing (investimento de ambas)
- Possibilidade de investimento cruzado
- Integração de marketplace completa
- Valor estimado: R$ 200-500K ano 1+

Cenário C (Strategic):
- SLABR adquire bynx.gg
- Operação como subsidiary com marca mantida
- Team bynx se torna parte de SLABR
- Diluição de equity: [A negociar]
- Valuation: [A negociar]

TIMELINE:
- Reunião esta semana para entender interesse
- NDA em 2 semanas
- Termo sheet em 4 semanas
- Implementação em 8-12 semanas

PRÓXIMOS PASSOS:
1. Vocês têm interesse em explorar essas oportunidades?
2. Qual seria o contato apropriado para discussão de negócio?
3. Qual é vosso timeline para decisões estratégicas?

Fico no aguardo.

Best regards,
[NOME]
VP Business Development, SLABR
```

---

## CHECKLIST PRÉ-CONTATO

Antes de enviar email, verifique:

- [ ] Identificar contato correto (partnerships, business, tech)
- [ ] Pesquisar bynx.gg no LinkedIn (founder, team)
- [ ] Verificar histórico de partnerships (se públicas)
- [ ] Entender pain points deles
- [ ] Preparar slide deck de 5-10 slides
- [ ] Ter números específicos (DAU, GMV, usuários)
- [ ] Preparar NDA (se necessário)
- [ ] Ter legal team ready para revisar termos

---

## POSSÍVEIS CONTATOS

Procure por:
- Founder/CEO bynx.gg (LinkedIn search)
- Business Development
- Tech Lead/CTO
- Product Manager

Canais:
- E-mail: partnerships@, business@, contact@ bynx.gg (testar variações)
- LinkedIn: Procurar por membros da empresa
- Twitter/X: @bynxgg (se existe)
- Site: Footer de bynx.gg (procure por links de contato)
- AngelList/Crunchbase: Se estão listados

---

## REUNIÃO KICKOFF - AGENDA PROPOSTA

Se conseguirem marcar a reunião, use esta agenda:

```
REUNIÃO SLABR + BYNX.GG PARTNERSHIP DISCUSSION
Duração: 45 minutos
Data: [TBD]
Participantes: 
  - SLABR: [CEO/CTO, PM, BD]
  - Bynx: [CEO/Founder, Tech Lead, Business Lead]

AGENDA:
(5 min) Apresentações
(10 min) Visão de cada empresa
(15 min) Oportunidade de partnership
  - Cenários de integração
  - Benefícios mútuos
  - Timeline
(10 min) Próximos passos
  - NDA
  - Technical spec sharing
  - Budget/Investment
(5 min) Fechamento

MATERIAIS PARA TRAZER:
- Slide deck SLABR (10-15 slides)
- Casos de uso de integração
- Roadmap de 12 meses
- Termos financeiros preliminares
- Contatos técnicos (emails)
```

---

## RESPOSTA ESPERADA - CENÁRIOS

### Cenário 1: Positivo
```
"Ótimo timing! Estávamos justamente pensando em 
expandir. Vamos marcar uma reunião com nosso CTO?"

AÇÃO:
→ Confirmar reunião técnica
→ Preparar spec detalhada
→ Engajar legal para NDA
```

### Cenário 2: Interessado mas Cauteloso
```
"Parece interessante. Podemos ter uma call 
para entender melhor?"

AÇÃO:
→ Preparar apresentação mais detalhada
→ Ter números/proofs prontos
→ Mostrar tração SLABR
→ Demonstrar sériedade
```

### Cenário 3: Não Interessado por Agora
```
"Interessante, mas focamos em nosso roadmap 
interno no momento."

AÇÃO:
→ Deixar porta aberta
→ Pedir para reconectar em 3-6 meses
→ Compartilhar plataforma SLABR
→ Build relationship
```

### Cenário 4: Resposta Negativa/Sem Resposta
```
(Sem resposta após 2 semanas)

AÇÃO:
→ Follow-up 1x em 1 semana
→ Tentar contato alternativo
→ Se ainda nada, aguardar 3 meses
→ Retentar depois
→ Considerar contato via LinkedIn
```

---

## DICAS PARA NEGOCIAÇÃO

### DO's:
- ✅ Seja claro sobre valor que traz
- ✅ Mostre números/tração de SLABR
- ✅ Responda rapidamente
- ✅ Seja flexível em termos
- ✅ Mantenha confidencialidade
- ✅ Respeite timeline deles
- ✅ Tenha legal review antes de assinar

### DON'Ts:
- ❌ Não pareça desperate
- ❌ Não compartilhe dados confidenciais
- ❌ Não pressione por resposta rápida
- ❌ Não copie features deles sem partnership
- ❌ Não vaze conversas público
- ❌ Não desista após "não" inicial
- ❌ Não faça promises que não pode cumprir

---

## TEMPLATE DE NDA (Simples)

```
CONFIDENTIALITY AGREEMENT

Between:
SLABR (Company A)
Bynx.gg (Company B)

1. Purpose: Discussion of potential partnership/integration

2. Confidentiality Period: 12 months from date of discussion

3. Excluded Information:
   - Public information
   - Information independently developed
   - Information rightfully received from third parties

4. Return of Information: Upon request or completion

5. No Obligation: Either party may discontinue discussions anytime

Both parties agree to keep all discussions confidential.

Assinado em: [DATA]
SLABR: [ASSINATURA]
Bynx: [ASSINATURA]
```

---

## TIMELINE RECOMENDADO

```
Semana 1:
└─ Identificar contato
└─ Preparar templates
└─ Enviar email 1 (Formal)

Semana 2:
└─ Follow-up se necessário
└─ Marcar reunião
└─ Preparar deck

Semana 3:
└─ Reunião de discussão
└─ Colher feedback
└─ Propor próximos passos

Semana 4:
└─ Enviar NDA (se interesse)
└─ Compartilhar spec técnica
└─ Agendar reunião técnica

Semana 5-6:
└─ Reunião técnica com CTO
└─ Discussão de termos financeiros
└─ Preparar contract

Semana 7+:
└─ Contract review (legal)
└─ Signatures
└─ Kick-off técnico
└─ Começar desenvolvimento
```

---

## RECURSOS ADICIONAIS

Para preparar negociação:
- [ ] Entender financeiro de SLABR (DAU, MRR, GMV)
- [ ] Preparar pitch em 1 minuto
- [ ] Preparar pitch em 5 minutos
- [ ] Preparar apresentação de 15 minutos
- [ ] Ter deck de 10 slides
- [ ] Ter video pitch (opcional)
- [ ] Ter case studies de partnership anterior

---

## EXEMPLO DE RESPOSTA ESPERADA

```
SLABR PARA BYNX.GG:

"Olá, tudo bem?

Somos uma plataforma brasileira de gerenciamento de coleções TCG. 
Admiramos o trabalho de vocês em Pokémon.

Gostaríamos de explorar uma partnership onde vocês são a fonte 
de dados oficial de preços em SLABR.

Vocês teriam interesse em uma conversa?

Obrigado,
SLABR Team"

RESPOSTA ESPERADA DE BYNX:

"Oi! Obrigado pelo interesse.

Sim, seria interessante explorar essa oportunidade. Qual seria 
o modelo? Podemos ter uma reunião?

Abraços,
Team Bynx"
```

---

**Use este template com confiança, mas adapte para seu estilo pessoal.**

**Boa sorte com a negotiação!** 🚀
