from flask import Flask, jsonify
import psycopg2
import boto3
import json
import os

app = Flask(__name__)

SECRET_NAME = "demo-eks-postgres"
REGION = "us-east-1"

def get_db_secret():
    client = boto3.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(response["SecretString"])

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/ready")
def ready():
    try:
        secret = get_db_secret()
        print("DEBUG DB USER:", secret["username"])

        conn = psycopg2.connect(
            host=secret["host"],
            port=secret["port"],
            user=secret["username"],
            password=secret["password"],
            dbname=secret["dbname"],
            connect_timeout=3
        )

        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]

        cur.close()
        conn.close()

        return jsonify(
            status="ready",
            db_version=version
        )

    except Exception as e:
        return jsonify(
            status="error",
            error=str(e)
        ), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
