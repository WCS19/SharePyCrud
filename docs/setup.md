# SharePyCrud Setup

Welcome to SharePyCrud! This document will guide you through setting up the project for development or usage.

---

## Prerequisites

Before proceeding, ensure you have the following installed:

- Python 3.11 or higher
- Git
- A virtual environment tool (e.g., `venv`)

---

## Step-by-Step Setup

### 1. Clone the Repository

Clone the SharePyCrud repository from GitHub:

```bash
git clone https://github.com/WCS19/SharePyCrud.git
cd SharePyCrud
```

### 2. Create a Virtual Environment

Set up a virtual environment to isolate your project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the SharePyCrud Package
Install the package in development mode:

```bash
pip install -e .
```

### 4. (Optional) Install Development Dependencies

If you are contributing to the project or require additional tools, install the development dependencies:

```bash
pip install -r dev-requirements.txt
```

### 5. Configure Environment Variables

The project requires specific environment variables for authentication with SharePoint. Use the provided .env.example file as a template:

&nbsp;&nbsp;&nbsp;&nbsp;1. Copy .env.example to .env:

```bash
cp .env.example .env
```

&nbsp;&nbsp;&nbsp;&nbsp;2. Edit the .env file with your SharePoint credentials and other necessary information.
Open the .env file and update the values:
```bash
SHAREPOINT__SITE=siteExample.sharepoint.com
CLIENT_ID=<your_client_id>
CLIENT_SECRET=<your_client_secret>
TENANT_ID=<your_tenant_id>
SHAREPOINT_URL=example.sharepoint.com
```

Replace the placeholder values with the appropriate credentials for your SharePoint instance.

---

## Next Steps

Now that you have set up SharePyCrud, you can start using it to interact with your SharePoint environment. Here are some suggested next steps:

1. Explore the examples provided in the `examples/` directory to learn how to perform common tasks. See the [README.md](README.md##Examples) for more information.

2. Refer to the [Documentation References](README.md#documentation-references) for additional context and guidance.

3. Contribute to the project! Check out the [CONTRIBUTING.md](CONTRIBUTING.md) file to learn how you can help improve SharePyCrud.
