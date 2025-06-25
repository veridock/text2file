"""Main entry point for the text2file package."""

def main():
    """Run the text2file CLI application."""
    from .cli import cli
    cli()


if __name__ == "__main__":
    main()
