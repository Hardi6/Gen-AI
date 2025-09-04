import boto3
import json

# Initialize Bedrock Runtime client
client = boto3.client("bedrock-runtime", region_name="ap-south-1")  # choose your region

model_id = "meta.llama3-8b-instruct-v1:0"

body = json.dumps({
    "prompt": "Explain how rainbows are formed",
    "temperature": 0.5,
    "top_p": 0.9,
    "max_gen_len": 200
})

response = client.invoke_model(
    modelId=model_id,
    body=body,
    accept="application/json",
    contentType="application/json"
)

result = json.loads(response["body"].read())
print(result["generation"] if "generation" in result else result)
