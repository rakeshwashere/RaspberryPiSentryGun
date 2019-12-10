rm SentryGunLambda.zip
zip -r SentryGunLambda.zip . -x \*.git\* \*.fuse*\*
aws lambda update-function-code --function-name SentryGunLamda --zip-file fileb://SentryGunLambda.zip