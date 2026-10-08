import marimo

__generated_with = "0.10.12"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(""" # Hello world!""")

    return (mo,)


if __name__ == "__main__":
    app.run()
