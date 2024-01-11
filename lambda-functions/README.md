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

When working locally, to get intellisense for your dependencies, create a venv in libraries_layer folder and install with pip.
.vscode/settings.json must include the path were your dependencies were installed.

## Secrets

Create a env.json file with the format specified in the example.env.json
The only variable that needs to be defined is Environment, the rest is handled by AWS Secrets Manager

`example-secrets-manager-keys.json` indicated the keys that should be available in the secrets manager.
Make sure a Secrets Manager exists in your AWS account with said keys.
Check `secrets_manager_helper.get_secrets()` for the naming convention of the secrets manager.
