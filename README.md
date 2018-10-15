# Kleeneup

Trabalho 1 de INE5421 - Linguagens Formais e Compiladores

Professora: Jerusa Marchi

Alunos: Cauê Baash de Souza e Caio Pereira Oliveira

Trabalho desenvolvido na linguagem Python (versão 3.5 e acima).

Instalação:
-----------

```bash
$ pip3 install --user kleeneup.whl
```

Execução:
---------
```bash
$ python3 -m kleeneup <argumentos>
```

Comandos disponíveis:
---------------------
```
Available commands:
  help             Displays help for a command
  list             Lists commands
 fa
  fa:create        Creates a stub file for a new automaton
  fa:determinize   Determinizes a finite automaton
  fa:evaluate      Evaluates a sentence using a finite automaton
  fa:intersection  Computes the intersection of two finite automata
  fa:minimize      Minimizes a finite automaton
  fa:rg            Converts an automaton to a regular grammar
  fa:union         Computes the union of two finite automata
 re
  re:fa            Converts a regular expression to a non-deterministic finite automaton
 rg
  rg:create        Creates a stub file for a new grammar
  rg:fa            Converts a grammar to a non-deterministic finite automaton
```

##### Exemplo de uso:
```bash
# Cria arquivo base para um autômato finito
$ python3 -m kleeneup fa:create mult3

# Edita arquivo do autômato
$ vim mult3.fa

# Testa se a palavra 110110 é aceita pelo autômato
$ python3 -m kleeneup fa:evaluate mult3 110110

# Minimiza autômato mult3 e salva em novo arquivo
$ python3 -m kleeneup fa:minimize mult3 mult3min
```
