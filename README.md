# bug-lang

This project uses [Poetry](https://python-poetry.org/) for dependency management and task automation.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Poetry installed on your machine. If you don't have it, you can install it by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

### Installing

To install the project dependencies, navigate to the project directory and run:

```bash
poetry install
```

This will read the pyproject.toml file and install the necessary dependencies.

### Running the tasks
The `pyproject.toml` file defines several tasks that can be run with Poetry:

- `lint`: This task runs the ruff linter on the project.
- `format`: This task formats the code using ruff.
- `type_check`: This task runs type checking on the project using pyright.
- `test`: This task runs the tests using pytest.
  
To run a task, use the following command:
```bash
poetry run task <task-name>
```

Replace `<task-name>` with the name of the task you want to run.

### Built With

- [Poetry](https://python-poetry.org/) - Dependency Management
- [Ruff](https://docs.astral.sh/ruff/) - Linter and formatter (replace with actual URL)
- [Pyright](https://github.com/microsoft/pyright) - Static type checker
- [pytest](https://pytest.org/) - Testing framework


### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### Grammar

- bee = var *
- silk = string
- ant = int
- flutter = float
- beetle = bool
- spider = if *
- web = else *
- fly = for *
- looper = while *
- spray = print *
- flick = fun *


### dejar el tac code y pasar directo a GO luego crear las dataclass para hacer la comparacion
