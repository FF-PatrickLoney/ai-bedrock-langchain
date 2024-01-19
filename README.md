# AI Bedrock Langchain

This is an investigation project to try out Amazon Bedrock and extends it's capabilities with Langchain.

## Run Locally

To start and test the project locally:

1. In the `/app` folder create a new python virtual env in a .venv folder.
2. Activate the new .venv using `source ./app/.venv/bin/activate`
3. Install dependencies using `pip install -r app/requirements.txt`
4. cd into the app folder.
5. Run local server with uvicorn: `python3 -m uvicorn main:app --env-file .env --reload`

Alternatively you can run the start.sh script:

`bash start.sh`

For both options make sure you are using your correct AWS_PROFILE (with access to Bedrock Models).

## Secrets

Create a env.json file with the format specified in the example.env.json
The only variable that needs to be defined is Environment, the rest is handled by AWS Secrets Manager.

Also, inside app, create a .env file for FastAPI.

`example-secrets-manager-keys.json` indicated the keys that should be available in the secrets manager.
Make sure a Secrets Manager exists in your AWS account with said keys.
Check `secrets_manager_helper.get_secrets()` for the naming convention of the secrets manager.

## Deployment

The first step is to make sure you have Docker installed and running, since we need a
Docker image to build the project.

After that, check that the template is valid by running:

```bash
sam validate
```

If the template doesn't have errors, we can start the deployment process,
first run sam build and then run the sam deploy command with the desired profile,
config env, and for the first deployment add the --guided option:

```bash
sam build --use-container
sam deploy --guided --profile=your-aws-profile-here --config-env=dev/prod
```
