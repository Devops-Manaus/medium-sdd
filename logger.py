from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from contextlib import contextmanager
import time


class PipelineLogger:

    def __init__(self):
        self.console = Console()

    def pipeline_start(self, ferramentas: str, contexto: str):
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold cyan]SDD Pipeline[/bold cyan]\n"
            f"[white]Ferramentas:[/white] [yellow]{ferramentas}[/yellow]\n"
            f"[white]Contexto:[/white]    [yellow]{contexto}[/yellow]",
            border_style="cyan"
        ))
        self.console.print()

    def section(self, number: int, total: int, title: str):
        self.console.print("[bold white]──────────────────────────────────────[/bold white]")
        self.console.print(
            f"[bold cyan][{number}/{total}][/bold cyan] [bold white]{title}[/bold white]"
        )

    @contextmanager
    def task(self, description: str):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task(description, total=None)
            start = time.time()
            try:
                yield progress
                elapsed = time.time() - start
                progress.stop()
                self.console.print(
                    f"   [green]✓[/green] {description} [dim]({elapsed:.1f}s)[/dim]"
                )
            except Exception as e:
                elapsed = time.time() - start
                progress.stop()
                self.console.print(
                    f"   [red]✗[/red] {description} [dim]({elapsed:.1f}s)[/dim] — [red]{e}[/red]"
                )
                raise

    def search_query(self, query: str):
        self.console.print(f"   [dim]🔍 {query}[/dim]")

    def search_done(self, tool: str, n_results: int, n_queries: int):
        self.console.print(
            f"   [green]✓[/green] [white]{tool}[/white] — "
            f"[cyan]{n_results} resultados[/cyan] de "
            f"[cyan]{n_queries} queries[/cyan]"
        )

    def iteration(self, current: int, total: int):
        self.console.print()
        self.console.print(f"   [bold]Iteração {current}/{total}[/bold]")

    def critic_passed(self, layer: str, warnings: list = None):
        self.console.print(f"   [green]✓ Critic ({layer}): aprovado[/green]")
        if warnings:
            for w in warnings:
                self.console.print(f"   [yellow]⚠ {w}[/yellow]")

    def critic_failed(self, problems: list):
        self.console.print(f"   [red]✗ Critic: {len(problems)} problema(s)[/red]")
        for p in problems:
            self.console.print(f"   [red]  • {p}[/red]")

    def memory_hit(self, lesson: str):
        self.console.print(f"   [magenta]💡 Memória: {lesson[:80]}[/magenta]")

    def saved(self, path: str):
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold green]✓ Concluído[/bold green]\n"
            f"[white]Salvo em:[/white] [cyan]{path}[/cyan]",
            border_style="green"
        ))

    def validation_report(self, result):
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="bold", width=4)
        t.add_column()

        for p in result.problems:
            t.add_row("[red]✗[/red]", f"[red]{p}[/red]")
        for w in result.warnings:
            t.add_row("[yellow]⚠[/yellow]", f"[yellow]{w}[/yellow]")
        if result.passed:
            t.add_row("[green]✓[/green]", "[green]Todas as validações passaram[/green]")

        self.console.print(t)

    def error(self, msg: str):
        self.console.print(f"\n[bold red]ERRO:[/bold red] [red]{msg}[/red]\n")

    def metrics(self, data: dict):
        t = Table(title="Métricas", border_style="dim")
        t.add_column("Campo", style="cyan")
        t.add_column("Valor", style="white")
        for k, v in data.items():
            t.add_row(str(k), str(v))
        self.console.print(t)