@echo off
echo Deploying to Google Cloud Run...
echo.
echo NOTE: Ensure you have the Google Cloud SDK installed and are logged in (gcloud auth login).
echo NOTE: Ensure you have created a project and selected it (gcloud config set project YOUR_PROJECT_ID).
echo.

set /p DEPLOY_CONFIRM=Are you ready to deploy? (Y/N): 
if /I "%DEPLOY_CONFIRM%" neq "Y" goto :EOF

echo.
echo Deploying...
gcloud run deploy tripmate-backend --source . --region us-central1 --allow-unauthenticated
echo.
echo Deployment command finished. If successful, copy the Service URL shown above.
pause
