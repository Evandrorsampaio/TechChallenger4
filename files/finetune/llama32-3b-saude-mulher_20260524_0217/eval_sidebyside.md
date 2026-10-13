# Avaliação base vs fine-tuned
Adapter: `/content/drive/MyDrive/AssistenteHospitalar/files/finetune/llama32-3b-saude-mulher_20260524_0217/adapter_final`

---

## [ginecologia_obstetricia]
**USER**: Qual é o princípio da cirurgia de controle de danos?

**BASE** (ROUGE-L 0.078):

O princípio da cirurgia de controle de danos (ou "princípio de minimização do dano") é um conceito fundamental na medicina e na ética clínica. Ele se refere ao objetivo de minimizar os danos ou consequências negativas associados a uma intervenção cirúrgica ou a qualquer outra ação médica.

O princípio da cirurgia de controle de danos é baseado no seguinte raciocínio:

1.  **Minimizar o dano**: A ideia é reduzir ao máximo as consequências negativas associadas à intervenção cirúrgica ou à ação médica.
2.  **Considerar as alternativas**: Antes de realizar uma intervenção cirúrgica, os profissionais de saúde devem considerar todas as alternativas possíveis que possam evitar ou minimizar os danos.
3.  **Priorizar a saúde do paciente**: O bem-estar e a saúde do paciente devem ser sempre priorizados, e as intervenções cirúrgicas devem ser realizadas apenas quando essencialmente necessárias.

Em resumo, o princípio da cirurgia de controle de danos é um princípio ético que orienta os profissionais de saúde a minimizar os danos associados às intervenções cirúrgicas e a qualquer outra ação médica.

**FINE-TUNED** (ROUGE-L 0.068):

O princípio da cirurgia de controle de danos é a prevenção de danos, a minimização dos danos e a reversão dos danos. Isso significa que a cirurgia de controle de danos deve ser realizada de forma a evitar danos adicionais, minimizar os danos existentes e, se possível, reversar os danos. É importante lembrar que a cirurgia de controle de danos é uma ferramenta para prevenir danos, não para causar danos. Portanto, é fundamental realizar a avaliação de riscos e benefícios antes de realizar qualquer procedimento. Além disso, é importante considerar as consequências de cada ato e tomar decisões que promovam a saúde e o bem-estar da pessoa. É fundamental também considerar as opções de tratamento disponíveis e escolher a melhor opção de acordo com as necessidades individuais. É importante lembrar que a cirurgia de controle de danos é uma ferramenta para prevenir danos, não para causar danos. Portanto, é fundamental realizar a avaliação de riscos e benefícios antes de realizar qualquer procedimento. Além disso, é importante considerar as consequências de cada ato e tomar decisões que promovam a saúde e o bem-estar da pessoa. É fundamental também considerar as opções de tratamento disponíveis e escolher a melhor opção de acordo com as necessidades individuais. É importante lembrar que a cirurgia de controle de danos é uma ferramenta para prevenir danos, não para causar danos. Portanto, é fundamental realizar a avaliação de riscos e benefícios antes de realizar qualquer procedimento. Além disso, é importante

**GOLD**:

Abreviar a laparotomia antes da depleção das reservas fisiológicas do paciente, para assim tratar a coagulopatia, a hipotermia e corrigir o distúrbio ácido básico na unidade de terapia intensiva.

---

## [violencia_domestica [SENSITIVE]]
**USER**: Como conduzir a escuta qualificada de uma paciente com suspeita de violência doméstica?

**BASE** (ROUGE-L 0.119):

A escuta qualificada é fundamental em casos de suspeita de violência doméstica, pois visa garantir a segurança da paciente e identificar possíveis ameaças. Aqui estão os passos a seguir:

1. **Preparação**:
   - Certifique-se de que você está em um ambiente seguro e privado.
   - Informe a paciente sobre o propósito da conversa e que tudo o que ela compartilhar será mantido em confidência.
   - Estabeleça um fluxo de comunicação aberto e respeitoso.

2. **Abordagem Inicial**:
   - Comece com uma abordagem gentil e empática, como: "Olá, estou aqui para ouvir e ajudar. Você se sente confortável em falar sobre o que está acontecendo?"
   - Evite fazer suposições ou julgamentos, e concentre-se em ouvir atentamente.

3. **Perguntas Abertas**:
   - Faça perguntas abertas que permitam à paciente compartilhar sua experiência sem sentir-se interrogada, como:
     - "O que aconteceu?"
     - "Como você se sentiu?"
     - "Quais são seus medos?"
   - Evite perguntas fechadas ou que possam ser interpretadas como acusatórias.

4. **Atenção aos Sinais de Alerta**:
   - Preste atenção a sinais de alerta, como:
     - Lesões físicas ou emocionais
     - Mudanças de comportamento ou humor
     - Evitação de contato visual ou distanciamento
   - Documente esses sinais, mas faça-o de forma discreta e respeitosa.

5. **Identificação

**FINE-TUNED** (ROUGE-L 0.136):

O profissional deve utilizar o Protocolo de Acolhimento à Mulher em Situação de Violência Doméstica, que inclui a escuta qualificada, a identificação dos sinais de alerta e a notificação obrigatória ao SINAN. Além disso, é importante lembrar que a escuta qualificada é um processo que envolve a atenção ao detalhe e a compreensão do contexto em que a paciente se encontra. É fundamental que o profissional esteja atento às necessidades específicas da paciente e forneça apoio adequado. Informe à paciente que pode entrar em contato com a Ligue 180 para obter apoio e orientação. Informe à paciente que pode entrar em contato com a Delegacia da Mulher para obter apoio e orientação. Informe à paciente que pode entrar em contato com o CVV 188 para obter apoio e orientação. Informe à paciente que pode entrar em contato com o CAPS para obter apoio e orientação. Informe à paciente que pode entrar em contato com o SAMU 192 para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de saúde local para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à criança e ao adolescente para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à mulher e ao menor para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à comunidade para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à população indígena para obter apoio

**GOLD**:

O profissional deve utilizar o kit padrão de coleta de vestígios e a ficha de atendimento à vítima de violência doméstica para coletar informações relevantes. Em seguida, deve oferecer apoio emocional e orientação à paciente, informando-a sobre os serviços disponíveis, como o Ligue 180 e o CVV 188.

---

## [ginecologia_obstetricia]
**USER**: Quais são as fases consideradas no segundo período do parto?

**BASE** (ROUGE-L 0.047):

Durante o segundo período do parto, as fases consideradas são:

1. **Primeira fase do segundo período**: Após a passagem do útero pela bexiga (úteroúrea), mas antes da passagem do útero pelo ânus (parto vaginal). Nesta fase, o parto é considerado "iniciado", mas ainda não concluído.

2. **Segunda fase do segundo período**: Após a passagem do útero pelo ânus (parto vaginal). Nesta fase, o parto é considerado "concluído".

É importante lembrar que o segundo período do parto é caracterizado por uma série de mudanças fisiológicas e físicas, incluindo a passagem do útero pela bexiga e pelo ânus, além de alterações na pressão arterial e na frequência cardíaca.

**FINE-TUNED** (ROUGE-L 0.033):

O segundo período do parto é dividido em três fases: a fase de transição, a fase de descarga e a fase de recuperação. A fase de transição ocorre aproximadamente entre os 30 e 40 minutos após o início do segundo período, enquanto a fase de descarga ocorre aproximadamente entre os 40 e 60 minutos após o início do segundo período. A fase de recuperação ocorre aproximadamente entre os 60 e 90 minutos após o início do segundo período. É importante notar que essas fases podem variar de pessoa para pessoa. Além disso, a fase de transição é caracterizada por uma diminuição da frequência das contrações, enquanto a fase de descarga é caracterizada por uma diminuição da intensidade das contrações. A fase de recuperação é caracterizada por uma diminuição da frequência e da intensidade das contrações, além de uma melhora da circulação e da respiração. É fundamental que a mulher se sinta confortável e segura durante essas fases. Se a mulher se sentir desconfortável ou em dor, é importante que ela seja encaminhada para avaliação e tratamento adequados. É também importante lembrar que a fase de transição é uma fase de transição, e não há necessidade de realizar procedimentos adicionais. A fase de descarga é uma fase de descarga, e não há necessidade de realizar procedimentos adicionais. A fase de recuperação é uma fase de recuperação, e não há necessidade de realizar procedimentos adicionais. É fundamental que a mulher se sinta confortável e segura durante essas fases. Se a mulher se sentir desconfortável ou em dor, é importante que ela seja encaminhada para avaliação e tratamento

**GOLD**:

Fase passiva/transição e Fase ativa.

---

## [violencia_domestica [SENSITIVE]]
**USER**: Como preencher a ficha de notificação compulsória (SINAN) em caso de violência?

**BASE** (ROUGE-L 0.170):

Lamento ter de abordar esse tópico. Preencher a ficha de notificação compulsória (SINAN) em caso de violência é uma etapa crucial para garantir a segurança e o bem-estar da vítima. Aqui estão os passos a seguir:

1. **Verifique se a vítima está estável**: Antes de iniciar o processo de notificação, verifique se a vítima está estável e não apresenta risco imediato.
2. **Coletar informações**: Coletar as seguintes informações:
	* Nome e endereço da vítima;
	* Data e hora do incidente;
	* Descrição do incidente (inclusão de detalhes sobre a violência);
	* Identificação do agressor (nome, idade, endereço, etc.);
	* Qualquer outro detalhe relevante.
3. **Preencher a ficha SINAN**: Utilize o formulário de notificação compulsória (SINAN) disponível no site do Ministério da Saúde ou na Secretaria Estadual de Saúde (SES). Preencha todos os campos obrigatórios.
4. **Incluir anexos**: Anexe qualquer documento relevante, como:
	* Comprovante de identidade da vítima;
	* Comprovante de tratamento médico;
	* Comprovante de hospitalização;
	* Quaisquer outros documentos relevantes.
5. **Assinar a declaração**: Assine a declaração de notificação compulsória (SINAN) e anexe-a ao formulário.
6. **Enviar a ficha**: Enviar a ficha SINAN para a Secretaria Estadual de Saúde (SES) ou para o centro de atendimento mais

**FINE-TUNED** (ROUGE-L 0.178):

O profissional deve preencher a ficha de notificação compulsória (SINAN) com os dados da paciente, incluindo a descrição da violência, os sinais de alerta e os recursos disponíveis. É importante notificar a autoridade competente e encaminhar a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e a disponibilidade de recursos. Encaminhe a paciente para o serviço de atendimento à vítima de violência. Informe a paciente sobre a importância da notificação e

**GOLD**:

O profissional deve preencher a ficha de notificação compulsória (SINAN) de acordo com o Protocolo de Notificação de Violência Doméstica, fornecendo informações sobre a paciente, a natureza da violência e o resultado do atendimento.

---

## [violencia_domestica [SENSITIVE]]
**USER**: Como conduzir a escuta qualificada de uma paciente com suspeita de violência doméstica?

**BASE** (ROUGE-L 0.121):

A escuta qualificada é fundamental em casos de suspeita de violência doméstica, pois visa garantir a segurança da paciente e identificar possíveis ameaças. Aqui estão os passos a seguir:

1. **Preparação**:
   - Certifique-se de que você está em um ambiente seguro e privado.
   - Informe a paciente sobre o propósito da conversa e que tudo o que ela compartilhar será mantido em confidência.
   - Estabeleça um fluxo de comunicação aberto e respeitoso.

2. **Abordagem Inicial**:
   - Comece com uma abordagem gentil e empática, como: "Olá, estou aqui para ouvir e ajudar. Você se sente confortável em falar sobre o que está acontecendo?"
   - Evite fazer suposições ou julgamentos, e concentre-se em ouvir atentamente.

3. **Perguntas Abertas**:
   - Faça perguntas abertas que permitam à paciente compartilhar sua experiência sem sentir-se interrogada, como:
     - "O que aconteceu?"
     - "Como você se sentiu?"
     - "Quais são seus medos?"
   - Evite perguntas fechadas ou que possam ser interpretadas como acusatórias.

4. **Atenção aos Sinais de Alerta**:
   - Preste atenção a sinais de alerta, como:
     - Lesões físicas ou emocionais
     - Mudanças de comportamento ou humor
     - Evitação de contato visual ou distanciamento
   - Documente esses sinais, mas faça-o de forma discreta e respeitosa.

5. **Identificação

**FINE-TUNED** (ROUGE-L 0.114):

O profissional deve utilizar o Protocolo de Acolhimento à Mulher em Situação de Violência Doméstica, que inclui a escuta qualificada, a identificação dos sinais de alerta e a notificação obrigatória ao SINAN. Além disso, é importante lembrar que a escuta qualificada é um processo que envolve a atenção ao detalhe e a compreensão do contexto em que a paciente se encontra. É fundamental que o profissional esteja atento às necessidades específicas da paciente e forneça apoio adequado. Informe à paciente que pode entrar em contato com a Ligue 180 para obter apoio e orientação. Informe à paciente que pode entrar em contato com a Delegacia da Mulher para obter apoio e orientação. Informe à paciente que pode entrar em contato com o CVV 188 para obter apoio e orientação. Informe à paciente que pode entrar em contato com o CAPS para obter apoio e orientação. Informe à paciente que pode entrar em contato com o SAMU 192 para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de saúde local para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à criança e ao adolescente para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à mulher e ao menor para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à comunidade para obter apoio e orientação. Informe à paciente que pode entrar em contato com o serviço de proteção à população indígena para obter apoio

**GOLD**:

O profissional de saúde deve realizar a escuta qualificada utilizando a escala de gravidade da violência doméstica, identificar os sinais de alerta e realizar a notificação compulsória ao SINAN.

---

## [ginecologia_obstetricia]
**USER**: Qual é o objetivo do acompanhamento pré-natal?

**BASE** (ROUGE-L 0.066):

O objetivo do acompanhamento pré-natal é garantir a saúde da mulher e do feto durante a gravidez, identificar possíveis complicações e promover uma gestão adequada do parto e pós-parto.

De acordo com a Organização Mundial da Saúde (OMS) e as diretrizes da Sociedade Brasileira de Ginecologia e Obstetrícia (SBGO), o acompanhamento pré-natal deve incluir:

1. Avaliação inicial: verificação da saúde da mulher, incluindo exames de sangue, avaliação da pressão arterial e do índice de massa corporal (IMC).
2. Monitoramento da saúde fetal: exames ultrassonográficos para verificar o desenvolvimento do feto e detectar possíveis anormalidades.
3. Avaliação do risco materno-fetal: verificação do risco de complicações durante a gravidez e o parto, incluindo a presença de doenças crônicas, como diabetes ou hipertensão.
4. Planejamento do parto: discussão com a mulher sobre os planos de parto, incluindo a escolha do local de nascimento e a opção de intervenção médica.
5. Educação e apoio: fornecimento de informações sobre a gravidez, o parto e a postura materna, além de apoio emocional e psicológico.

A seguir estão os critérios objetivos para o acompanhamento pré-natal, conforme estabelecidos pela SBGO:

* Acompanhamento pré-natal deve ocorrer entre as 8ª e 12ª semanas de gravidez.
* A mulher deve ser verificada pelo menos uma vez por mês durante a gravidez.
* O acompanhamento pré-natal

**FINE-TUNED** (ROUGE-L 0.119):

O objetivo do acompanhamento pré-natal é fornecer cuidados de saúde adequados às mulheres durante a gestação, identificar riscos e problemas potenciais, e desenvolver estratégias para prevenir e tratar esses problemas. Além disso, o acompanhamento pré-natal também visa fornecer informações e apoio às mulheres e suas famílias sobre a gestação, o parto e a amamentação. Isso inclui orientações sobre alimentação, atividade física, sono e outros aspectos da saúde materna. O acompanhamento pré-natal também pode incluir a realização de exames e testes de rotina, como ultrassonografia, hemograma e glicemia de jejum, além de consultas com especialistas, como obstetras e ginecologistas. É importante que as mulheres tenham acesso a cuidados de saúde de qualidade e que os profissionais de saúde estejam treinados para fornecer esses cuidados. O acompanhamento pré-natal é fundamental para garantir a saúde e o bem-estar das mulheres durante a gestação.

**GOLD**:

Assegurar o desenvolvimento da gestação, permitindo o parto de um recém-nascido saudável, sem impacto para a saúde materna.

---

## [ginecologia_obstetricia]
**USER**: Em que período gestacional deve ser realizada a ecocardiografia fetal?

**BASE** (ROUGE-L 0.144):

De acordo com as diretrizes clínicas, a ecocardiografia fetal deve ser realizada em todas as gestações, mas com maior frequência em períodos específicos:

*   **1º trimestre**: É recomendável realizar a ecocardiografia fetal entre 8 e 12 semanas de gestação, pois nesse período é mais fácil detectar anormalidades cardíacas.
*   **2º e 3º trimestres**: A ecocardiografia fetal também deve ser realizada em esses períodos, especialmente se houver sintomas maternos ou fetais que possam indicar problemas cardíacos.

No entanto, é importante notar que a escolha do período ideal para a ecocardiografia fetal pode variar dependendo das circunstâncias individuais e da avaliação clínica do paciente.

**FINE-TUNED** (ROUGE-L 0.031):

Entre 16 e 20 semanas de gestação. É importante realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para monitorar o crescimento e desenvolvimento do feto durante a gestação. É recomendável realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para monitorar o crescimento e desenvolvimento do feto durante a gestação. É recomendável realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para monitorar o crescimento e desenvolvimento do feto durante a gestação. É recomendável realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para monitorar o crescimento e desenvolvimento do feto durante a gestação. É recomendável realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para monitorar o crescimento e desenvolvimento do feto durante a gestação. É recomendável realizar essa ultrassonografia entre 16 e 20 semanas de gestação, pois é fundamental para detectar possíveis problemas cardíacos no feto. Além disso, é uma ferramenta valiosa para

**GOLD**:

A ecocardiografia fetal deve ser realizada entre 11 e 14 semanas.

---

## [violencia_domestica [SENSITIVE]]
**USER**: Quais critérios indicam internação psiquiátrica involuntária?

**BASE** (ROUGE-L 0.206):

A internação psiquiátrica involuntária é uma medida implementada para proteger a saúde mental de indivíduos que apresentam risco de autoagressão ou de perigo para os outros. Os critérios que indicam a necessidade de internação psiquiátrica involuntária são estabelecidos pela Organização Mundial da Saúde (OMS) e pela Sociedade Brasileira de Psiquiatria (SBP), entre outras entidades.

Segundo a SBP, os critérios para internação psiquiátrica involuntária incluem:

1. **Risco de autoagressão**: O indivíduo apresenta comportamento agressivo, como ameaças, agressão física ou verbal, contra si mesmo ou outros.
2. **Risco de perigo para os outros**: O indivíduo apresenta comportamento que possa causar dano a si mesmo ou a terceiros, como tentativas de suicídio, automutilação ou agressão física.
3. **Distúrbio psicótico**: O indivíduo apresenta sintomas psicóticos, como alucinações, delírios ou pensamentos desorganizados.
4. **Esquizofrenia aguda**: O indivíduo apresenta sintomas de esquizofrenia, como alucinações, delírios ou pensamentos desorganizados, que requerem intervenção imediata.
5. **Crisis de pânico**: O indivíduo apresenta sintomas de pânico, como ansiedade extrema, hiperventilação ou tremores, que requerem intervenção imediata.
6. **Depressão severa**: O indiv

**FINE-TUNED** (ROUGE-L 0.221):

O profissional deve considerar critérios como risco de lesão física ou psicológica para a paciente ou terceiros, incapacidade de cuidar de si mesma, ou necessidade de tratamento psiquiátrico imediato. É importante realizar uma avaliação cuidadosa e considerar a necessidade de internação psiquiátrica involuntária. Informe a paciente sobre a importância de procurar ajuda e ofereça apoio emocional. Encaminhe a paciente para a Rede de Atenção Psiquiátrica (RAP) ou para o Serviço de Atendimento Psiquiátrico (SAP). Informe a paciente sobre a disponibilidade do Ligue 180 e CVV 188 para obter apoio emocional e orientação. Encaminhe a paciente para a Delegacia da Mulher ou Conselho Tutelar para obter apoio legal e proteção. É fundamental respeitar a autonomia da paciente e oferecer apoio emocional e orientação. Encaminhe a paciente para a Rede de Atenção Psiquiátrica (RAP) ou para o Serviço de Atendimento Psiquiátrico (SAP) para obter tratamento psiquiátrico adequado. Informe a paciente sobre a importância de procurar ajuda e ofereça apoio emocional. Encaminhe a paciente para a Rede de Atenção Psiquiátrica (RAP) ou para o Serviço de Atendimento Psiquiátrico (SAP) para obter tratamento psiquiátrico adequado. Informe a paciente sobre a disponibilidade do Ligue 180 e CVV 188 para obter apoio emocional e orientação. Encaminhe

**GOLD**:

O profissional deve considerar a necessidade de internação psiquiátrica involuntária se a paciente apresentar risco de suicídio ou lesão física, ou se estiver em estado de confusão ou alucinação. Em casos de violência doméstica, a internação pode ser indicada se a paciente estiver em estado de agitação ou se houver suspeita de lesão física grave.

---

## [saude_mental [SENSITIVE]]
**USER**: Quais sinais de alerta para risco de suicídio devo identificar na anamnese?

**BASE** (ROUGE-L 0.213):

Ao realizar a anamnese de uma paciente com sintomas relacionados à saúde da mulher, é fundamental identificar sinais de alerta para risco de suicídio. Aqui estão alguns critérios e sinais de alerta que você deve considerar:

**Sinais de alerta para risco de suicídio:**

1. **Comportamento de isolamento social**: Paciente que evita contato com amigos e familiares.
2. **Comportamento de depressão**: Paciente que apresenta sintomas de depressão, como perda de interesse em atividades, mudanças no humor, etc.
3. **Comportamento de ansiedade**: Paciente que apresenta sintomas de ansiedade, como pânico, medo, etc.
4. **Histórico de tentativas de suicídio**: Paciente que já tentou suicídio anteriormente.
5. **Comportamento de abstinência**: Paciente que apresenta sintomas de abstinência, como depressão, irritabilidade, etc.
6. **Comportamento de perda de interesse**: Paciente que apresenta perda de interesse em atividades que costumava gostar.
7. **Comportamento de mudanças no sono**: Paciente que apresenta alterações no sono, como insônia ou hipersomnia.
8. **Comportamento de alterações no apetite**: Paciente que apresenta alterações no apetite, como aumento ou diminuição do apetite.

**Critérios de avaliação:**

1. **Perguntas abertas**: Faça perguntas abertas para entender melhor a situação do paciente, como "Como você se sente atualmente?" ou "O que está pensando?"
2. **Escala de avaliação de depressão**:

**FINE-TUNED** (ROUGE-L 0.252):

O profissional deve identificar sinais de alerta como história de tentativas de suicídio, pensamentos suicidas atuais, plano de suicídio, meios para suicídio, isolamento social, perda de interesse em atividades, mudanças no sono ou apetite, e outros sintomas depressivos. É importante lembrar que a identificação desses sinais não é suficiente para prevenir o suicídio, e que a paciente deve ser encaminhada para avaliação psicológica e tratamento adequados. Informe à paciente que pode entrar em contato com o Ligue 180 (0800 180) ou o CVV 188 (188) para obter apoio e orientação. Além disso, é importante lembrar que a paciente pode ter direito a tratamento psicológico e/ou medicamentoso, dependendo da gravidade do risco de suicídio. Informe à paciente que pode entrar em contato com o CAPS (Centro de Atenção Psicossocial) para obter avaliação e tratamento psicológico. É importante lembrar que a paciente pode ter direito a acompanhante durante a consulta, se necessário. Informe à paciente que pode entrar em contato com o SAMU 192 (192) para obter apoio e orientação em caso de emergência. Informe à paciente que pode entrar em contato com a Delegacia da Mulher para obter apoio e orientação em caso de violência. É importante lembrar que a paciente pode ter direito a acompanhante durante a consulta, se necessário. Informe à paciente que pode entrar em contato com o CVV 188 (188) para obter apoio e orientação. Informe à paciente que pode entrar em contato com o

**GOLD**:

O profissional deve estar atento a sinais de alerta como histórico de tentativas de suicídio, pensamentos suicidas atuais, isolamento social, perda de interesse em atividades, mudanças no padrão de sono ou apetite, e aumento do consumo de álcool ou outras substâncias. Em caso de suspeita, é fundamental acionar o SAMU 192 ou a Unidade de Emergência Psiquiátrica mais próxima.

---

## [planejamento_familiar]
**USER**: Quais tipos de NSAID podem proporcionar alívio de sintomas para dor pélvica?

**BASE** (ROUGE-L 0.029):

Para o alívio de sintomas de dor pélvica, os anti-inflamatórios não esteroides (NSAID) podem ser uma opção. No entanto, é importante considerar as seguintes opções:

- **Ibuprofeno (Advil, Motrin)**: Dose recomendada para dor pélvica é de 400 mg a 600 mg, 2 a 3 vezes ao dia, conforme necessário.
- **Naproxeno (Aleve)**: Dose recomendada para dor pélvica é de 250 mg a 500 mg, 2 a 3 vezes ao dia, conforme necessário.
- **Ketorolac (Toradol)**: Dose recomendada para dor pélvica é de 10 mg a 20 mg, 3 vezes ao dia, conforme necessário.

É fundamental lembrar que a dosagem e a frequência podem variar dependendo da gravidade da dor e da resposta individual do paciente. Além disso, é importante considerar a prescrição médica antes de iniciar qualquer tratamento com NSAID, pois eles podem ter efeitos colaterais e interagir com outros medicamentos.

Em casos de dor pélvica aguda, pode ser recomendado o uso de NSAID por um período limitado (geralmente 7 a 10 dias). Em casos crônicos, pode ser necessário considerar outras opções de tratamento, como fármacos específicos para dor pélvica ou terapias comportamentais.

**FINE-TUNED** (ROUGE-L 0.007):

NSAIDs como ibuprofeno, naproxeno, diclofenaco e aspirina podem proporcionar alívio de sintomas para dor pélvica. É importante consultar um profissional de saúde antes de iniciar qualquer tratamento. Além disso, é fundamental considerar a prescrição de NSAIDs para mulheres com dor pélvica, especialmente aquelas com história de violência doméstica ou sexual. É recomendável encaminhar as mulheres para avaliação médica e tratamento adequados. Informe a paciente sobre a importância de consultar um profissional de saúde antes de iniciar qualquer tratamento. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a disponibilidade de serviços de apoio, como o Ligue 180 e o CVV 188. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a importância de consultar um profissional de saúde antes de iniciar qualquer tratamento. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a disponibilidade de serviços de apoio, como o Ligue 180 e o CVV 188. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a importância de consultar um profissional de saúde antes de iniciar qualquer tratamento. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a disponibilidade de serviços de apoio, como o Ligue 180 e o CVV 188. Encaminhe a paciente para avaliação médica e tratamento adequados. Informe a paciente sobre a importância de consultar um profissional de saúde antes de iniciar qualquer tratamento. Encaminhe a paciente para avaliação médica

**GOLD**:

Diclofenac 100 mg, meclofenamate sódico 100 mg e 200 mg
