from os import environ
import json

import boto3

echocore_zip = None
with open("echocore.zip", "rb") as f:
    echocore_zip = f.read()

layer_name = f'echocore-{environ["VERSION"].replace(".", "_")}'
echocore_arns = dict()
for region_name in ("us-east-1", "us-east-2", "us-west-1", "us-west-2"):
    print(f"Publishing {layer_name} to {region_name}")
    lambda_client = boto3.client("lambda", region_name=region_name)
    response = lambda_client.publish_layer_version(
        CompatibleArchitectures=["x86_64"],
        CompatibleRuntimes=["python3.9"],
        Content=dict(ZipFile=echocore_zip),
        Description="Core Python packages for EchoStream lambda functions",
        LayerName=layer_name,
        LicenseInfo="APL2",
    )
    lambda_client.add_layer_version_permission(
        Action="lambda:GetLayerVersion",
        LayerName=response["LayerArn"],
        Principal="*",
        StatementId="PublicAccess",
        VersionNumber=response["Version"],
    )
    if response["Version"] != 1:
        try:
            lambda_client.delete_layer_version(
                LayerName=response["LayerArn"],
                VersionNumber=response["Version"]-1,
            )
        except Exception:
            print(f'WARNING: Unable to delete version {response["Version"]} for {layer_name}')
    echocore_arns[region_name] = response["LayerVersionArn"]
with open("echocore.json", "wt") as f:
    json.dump(echocore_arns, f, separators=(",", ":"))
