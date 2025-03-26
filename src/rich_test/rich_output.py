from datetime import datetime

from rich.console import Console
from rich.table import Table

# Initialize the Console
console = Console()

# Print a rule with the current date and time
console.rule(f"[bold red]Report Generated {datetime.now().ctime()}[/bold red]")

# Create a table
table = Table(title="Sample Table")

# Add columns
table.add_column("ID", style="cyan", justify="right")
table.add_column("Name", style="magenta")
table.add_column("Status", style="green")

# Add rows
table.add_row("1", "Task A", "Complete")
table.add_row("2", "Task B", "In Progress")
table.add_row("3", "Task C", "Pending")

# Print the table
console.print(table)

# Print some colored text
console.print("[bold blue]End of Report[/bold blue]")
