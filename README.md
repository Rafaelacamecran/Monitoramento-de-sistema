# Nome do projeto:
Monitoramento de sistema

# Descrição:
Este projeto é uma ferramenta de utilidade para o sistema Windows, desenvolvida em Python, que combina várias funcionalidades principais numa única aplicação com interface gráfica:
Monitoramento de Desempenho em Tempo Real e Fornece um painel que exibe dados vitais do sistema, atualizados a cada 2 segundos e as métricas monitoradas incluem o uso da CPU (em percentagem), o uso da Memória RAM (percentagem e GB) e o uso do Disco (percentagem e GB)
Análise e Limpeza de Arquivos (com Modo de Simulação):
A) Escaneamento Inteligente: A aplicação pode varrer diretórios comuns do sistema (como pastas temporárias e a pasta de Downloads) para identificar arquivos que podem ser desnecessários e B) Classificação por Cores: Durante o escaneamento, os arquivos são classificados e exibidos com cores distintas para fácil identificação: Vermelho para arquivos "suspeitos" como logs antigos, backups (.bak) e arquivos temporários (.tmp), Laranja para arquivos "desnecessários" como ficheiros muito grandes na pasta de Downloads ou outros itens temporários e Verde para arquivos comuns considerados seguros, B) Feedback Visual em Tempo Real: Enquanto o escaneamento está ocorrendo, o nome do arquivo que está sendo analisado é exibido e a sua cor muda instantaneamente de acordo com a sua classificação, C) Modo de Simulação (Segurança em Primeiro Lugar): A funcionalidade mais importante desta aba é que ela opera num modo de simulação, isto significa que nenhuma ação de exclusão de arquivos é realmente executada, apenas simulada, para apagar arquivos de verdade, o utilizador precisa desmarcar ativamente a opção e confirmar um aviso de segurança, D) Exclusão Seletiva: O botão de "Apagar" foi projetado para remover apenas os arquivos classificados como "suspeitos" (vermelhos), tornando o processo mais seguro e E) Relatórios Detalhados: Após o escaneamento, é possível gerar um relatório em formato CSV com a lista completa de todos os arquivos encontrados e um arquivo de log (.txt) que regista todas as ações executadas pela aplicação.

# Funcionalidades:
Este projeto é uma ferramenta 2 em 1 para Windows que permite:
Monitoriza o PC: Mostra em tempo real o uso do CPU, Memória RAM e Disco para que possa ver o quão "ocupado" o seu computador está, Analisa e Limpa Ficheiros: escaneia pastas comuns em busca de ficheiros desnecessários ou "lixo digital", Classifica os ficheiros por cores: Vermelho para os suspeitos, Laranja para os desnecessários e Verde para os seguros e a sua principal vantagem é a segurança, pois funciona num modo de simulação que não apaga nada, apenas mostra o que faria. Para uma limpeza real, o utilizador tem de desativar este modo de segurança.
No final, pode gerar relatórios em CSV e TXT de tudo o que foi encontrado e feito para uma futura auditoria e análise dos relatórios.

# # Tecnologias usadas:
Linguagem Python
