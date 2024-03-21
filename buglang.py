import click
from bug_lang.context import Context
from rich.console import Console
from rich.syntax import Syntax
from tabulate import tabulate

# Define the command-line interface using Click decorators
@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('-l', '--lex', is_flag=True, help='Display tokens from lexer')
@click.option('-a', '--AST', is_flag=True, help='Display AST')
@click.option('-D', '--dot', is_flag=True, help='Generate AST graph as DOT format')
@click.option('--sym', is_flag=True, help='Dump the symbol table')  # the Checker one
@click.option('-R', '--exec', 'execute', is_flag=True, help='Execute the generated program')
def main(input_file, lex, ast, dot, sym, execute):
    console = Console()

    console.print("\t\t\t\n[bold green]################################ Bug-lang Compiler ################################[/bold green]\n")
    ctxt = Context()
    source = input_file.read()
    ctxt.parse(source)

    if lex:
        console.print("\n\n[bold blue]********** TOKENS **********[/bold blue]\n")
        tokens = ctxt.lexer.tokenize(source)
        table = [["Type", "Value", "At line"]]
        for tok in tokens:
            row = [tok.type, tok.value, tok.lineno]
            table.append(row)
        console.print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

    if ast:
        console.print("\n\n[bold magenta]********** AST **********[/bold magenta]\n")
        ast_syntax = Syntax(str(ctxt.ast), "python", theme="ansi_dark", line_numbers=True)
        console.print(ast_syntax)

    if dot:
        console.print("\n\n[bold cyan]DOT LANGUAGE[/bold cyan]\n")
        dot = DotRender.render(ctxt.ast)  # render
        console.print(dot)

    if sym:
        console.print("\n[bold yellow]Symbol Table[/bold yellow]\n")
        console.print(ctxt.interp.env)

    if execute:
        ctxt.run()

if __name__ == "__main__":
    main()
