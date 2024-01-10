## Run Locally

To start and test your Lambda Functions locally:

1. Make sure you have docker installed in your machine.

2. Make sure you are in the lambda-functions folder.

```bash
  cd lambda-functions
```

3. Run sam build

```bash
  sam build
```

4. In a separate terminal, in the same folder, run:

```bash
  sam local start-api --profile=your-aws-profile-here --env-vars=path-to-local-env.json-file
```

5. Every time you need to test updated code changes, re-run sam build in your first terminal.

## Local Dependencies and Intellisense

When working locally, to get intellisense for your dependencies, create a venv in the functions folder and install requirements with pip.
