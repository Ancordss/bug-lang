import webbrowser

import click
from rich.console import Console
from rich.syntax import Syntax
from tabulate import tabulate
from rich.table import Table
from rich.markdown import Markdown

from bug_lang.context import Context


# Define the command-line interface using Click decorators
@click.command()
@click.argument("input_file", type=click.File("r"))
@click.option("-l", "--lex", is_flag=True, help="Display tokens from lexer")
@click.option("-a", "--AST", is_flag=True, help="Display AST")
@click.option("-D", "--dot", is_flag=True, help="Generate AST graph as DOT format")
@click.option("-s", "--sym", is_flag=True, help="Dump the symbol table")  # the Checker one
@click.option("-R", "--exec", "execute", is_flag=True, help="Execute the generated program")
@click.option("-er", "--errors", is_flag=True, help="Export errors to HTML file")
def main(input_file, lex, ast, dot, sym, execute, errors):
    console = Console(record=True)

    console.print(
        "\t\t\t\n[bold green]################################ Bug-lang Compiler ################################[/bold green]\n"
    )
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
        console.print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
        html_output = console.export_html()

        # Guardar la salida HTML en un archivo
        with open("output.html", "w", encoding="utf-8") as html_file:
            html_file.write(html_output)

        # Abrir el archivo en el navegador
        webbrowser.open("output.html")

    if ast:
        console.print("\n\n[bold magenta]********** AST **********[/bold magenta]\n")
        ast_syntax = Syntax(str(ctxt.ast), "python", theme="ansi_dark", line_numbers=True)
        console.print(ast_syntax)

    if dot:
        console.print("\n\n[bold cyan]DOT LANGUAGE[/bold cyan]\n")
        dot = DotRender.render(ctxt.ast)  # render
        console.print(dot)

    # if sym:
    #     console.print("\n[bold yellow]Symbol Table[/bold yellow]\n")
    #     console.print(ctxt.tb_sym())

    if execute:
        if sym:
            ctxt.run(sym)
        else:
            ctxt.run(None)

    if errors and ctxt.have_errors:
        console.print("\n[bold red]PARSER AND LEXER ERRORS[/bold red]")
        error_table = Table(title="Compilation Errors", show_header=True, header_style="bold magenta")
        error_table.add_column("Error Details", style="red")
        for error in ctxt.errors:
            error_table.add_row(error)
        console.print(error_table)
        html_output = console.export_html()
        with open("errors_output.html", "w", encoding="utf-8") as html_file:
            html_file.write(html_output)
        webbrowser.open("errors_output.html")


if __name__ == "__main__":
    main()
