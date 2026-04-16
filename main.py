import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from pipeline import SDDPipeline

load_dotenv()
console = Console()

DEFAULT_SECTIONS = [
    "tldr", "what_is", "requirements", "installation",
    "configuration", "practical_example", "pitfalls",
    "optimizations", "conclusion", "references",
]

AVAILABLE_FOCUSES = [
    "general comparison",
    "performance / throughput",
    "cost",
    "migration",
    "integration",
    "security",
    "limited hardware / edge",
    "quantization / local models",
]


def ask_focus() -> str:
    console.print("\n[dim]Available focuses:[/dim]")
    for i, f in enumerate(AVAILABLE_FOCUSES, 1):
        console.print(f"  [cyan]{i}.[/cyan] {f}")

    choice = Prompt.ask(
        "\n[bold]Research focus[/bold] [dim](number or free text, enter for default)[/dim]",
        default="",
    )

    if not choice.strip():
        return "general comparison"

    if choice.strip().isdigit():
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(AVAILABLE_FOCUSES):
            return AVAILABLE_FOCUSES[idx]

    return choice.strip()


def ask_questions() -> list[str]:
    console.print("\n[dim]Type questions that the article MUST answer.")
    console.print("[dim]Be specific — the model will use this directly.")
    console.print("[dim]Empty enter to finish.\n")
    console.print("[dim]Examples:[/dim]")
    console.print("[dim]  → how to configure rootless mode?[/dim]")
    console.print("[dim]  → does docker-compose work without changes?[/dim]")
    console.print("[dim]  → which has the lowest RAM usage at idle?[/dim]\n")

    items = []
    i = 1
    while True:
        q = Prompt.ask(f"  [cyan]Question {i}[/cyan]", default="")
        if not q.strip():
            break
        items.append(q.strip())
        i += 1
    return items


def collect_validations() -> list[str]:
    console.print("\n[dim]Type criteria that the article MUST contain.")
    console.print("[dim]Empty enter to finish.\n")

    items = []
    i = 1
    while True:
        v = Prompt.ask(f"  [cyan]Criterion {i}[/cyan]", default="")
        if not v.strip():
            break
        items.append(v.strip())
        i += 1
    return items


def display_summary(tools, context, focus, questions, validations):
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column(style="dim", width=16)
    t.add_column(style="white")

    t.add_row("Tools", f"[yellow]{tools}[/yellow]")
    t.add_row("Context",    f"[yellow]{context}[/yellow]")
    t.add_row("Focus",        f"[cyan]{focus}[/cyan]")
    t.add_row(
        "Article should\nanswer",
        "\n".join(f"→ {q}" for q in questions) if questions else "[dim]no additional questions[/dim]",
    )
    t.add_row(
        "Validations",
        "\n".join(f"☐ {v}" for v in validations) if validations else "[dim]none[/dim]",
    )

    console.print()
    console.print(Panel(t, title="[bold cyan]Summary[/bold cyan]", border_style="cyan"))
    console.print()


def post_execution_checklist(validations: list[str], output_path: str):
    if not validations:
        return

    console.print(Panel.fit(
        "[bold white]Manual validation checklist[/bold white]",
        border_style="yellow",
    ))
    console.print(f"[dim]Article: {output_path}[/dim]\n")

    approved = 0
    for v in validations:
        ok = Confirm.ask(f"  [white]{v}[/white]")
        if ok:
            approved += 1
            console.print("  [green]✓[/green]\n")
        else:
            console.print("  [red]✗[/red]\n")

    total = len(validations)
    color = "green" if approved == total else "yellow" if approved > 0 else "red"
    console.print(f"[{color}]Result: {approved}/{total} criteria met[/{color}]\n")


def main():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SDD Tech Writer[/bold cyan]\n"
        "[dim]Technical article generation with local LLM[/dim]",
        border_style="cyan",
    ))
    console.print()

    try:
        tools = Prompt.ask("[bold]Tools[/bold] [dim](ex: podman and docker)[/dim]")
        context    = Prompt.ask("[bold]Context[/bold]    [dim](ex: local dev environment on Linux)[/dim]")
        focus        = ask_focus()
        questions    = ask_questions()
        validations  = collect_validations()
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled.[/dim]")
        sys.exit(0)

    display_summary(tools, context, focus, questions, validations)

    if not Confirm.ask("[bold]Start pipeline?[/bold]", default=True):
        console.print("[dim]Cancelled.[/dim]")
        sys.exit(0)

    pipeline    = SDDPipeline()
    output_path = pipeline.run(
        tools=tools,
        context=context,
        focus=focus,
        questions=questions,
    )

    post_execution_checklist(validations, output_path)


if __name__ == "__main__":
    main()
