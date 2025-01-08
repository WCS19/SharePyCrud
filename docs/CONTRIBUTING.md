# Contributing to SharePyCrud

Thank you for considering contributing to SharePyCrud! Your contributions help make this project better for everyone. Whether you’re fixing bugs, adding features, or improving documentation, I appreciate your efforts. Below are the guidelines for contributing to this project.

---

## Getting Started

1. **Fork the Repository**:
   - Navigate to the [SharePyCrud GitHub page](https://github.com/WCS19/SharePyCrud).
   - Click the `Fork` button to create your own copy of the repository.

2. **Clone the Fork**:
   - Clone your fork to your local machine:
     ```bash
     git clone https://github.com/<your-username>/SharePyCrud.git
     cd SharePyCrud
     ```

3. **Set Up the Environment**:
   - Follow the setup instructions in the [SETUP.md](setup.md) file to configure your development environment.

4. **Add Upstream Remote**:
   - Add the original repository as an upstream remote to keep your fork updated:
     ```bash
     git remote add upstream https://github.com/WCS19/SharePyCrud.git
     ```

---

## Development Workflow

1. **Create a Branch**:
   - Create a new branch for your feature or bug fix:
     ```bash
     git checkout -b feature/your-feature-name
     ```
     Use a descriptive branch name, such as `fix/auth-bug` or `feature/add-update-support`.

2. **Make Your Changes**:
   - Implement your changes in the appropriate files.
   - Follow the existing code style. Use `black` for formatting:
     ```bash
     black src/
     ```

3. **Write Tests**:
   - Add or update tests to ensure your changes work as intended. Use `pytest` to run the tests:
     ```bash
     pytest
     ```

4. **Commit Changes**:
   - Commit your changes with a clear and descriptive message:
     ```bash
     git add .
     git commit -m "Add feature to support CRUD operations for SharePoint lists"
     ```

5. **Push Changes**:
   - Push your branch to your fork:
     ```bash
     git push origin feature/your-feature-name
     ```

6. **Create a Pull Request**:
   - Open a pull request from your branch to the `main` branch of the original repository.
   - Include a clear description of the changes, why they were made, and any relevant issues (e.g., "Fixes #123").

---

## Guidelines for Contributions

1. **Code Style**:
   - Use `black` for code formatting.
   - Use `mypy` for static type checking:
     ```bash
     python -m mypy . --strict
     ```

2. **Documentation**:
   - Update the `README.md` or add documentation for any new features.
   - Ensure any new environment variables, configuration options, or setup steps are documented in `SETUP.md`.

3. **Tests**:
   - Ensure all new functionality is covered by tests.
   - Avoid regressions by running all existing tests.

4. **Commit Messages**:
   - Use descriptive commit messages in the imperative tone, e.g., `Add support for custom authentication`.

5. **Communication**:
   - For major changes or feature ideas, open an issue to discuss before starting development.

---

## Reporting Issues

If you encounter a bug or have a feature request:
1. Check the [issues page](https://github.com/WCS19/SharePyCrud/issues) to see if it’s already reported.
2. If not, open a new issue with:
   - A clear and descriptive title.
   - Steps to reproduce the issue, if applicable.
   - Expected vs. actual behavior.
   - Any relevant logs or screenshots.


---

I appreciate your contributions! Thank you for helping improve SharePyCrud. 🚀
