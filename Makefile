CLEANFILE_SRC = clean.bat
GRAMMAR_FILE = grammar.y
LEXICAL_FILE = lexical.l
# all: Bison flex gcc run (old)
all: Bison flex buildcpp run
Bison:
	bison -d $(GRAMMAR_FILE)

flex:
	flex $(LEXICAL_FILE)

gcc:
	gcc -c lex.yy.c -o lex.yy.o
	gcc -c grammar.tab.c -o grammar.tab.o
	gcc lex.yy.o grammar.tab.o -o myParser.exe

run:
	./myParser.exe test.bug

cl:
	$(CLEANFILE_SRC)
