resource "aws_secretsmanager_secret" "db_secret" {
  name = "${var.cluster_name}-db-credentials"
}

resource "aws_secretsmanager_secret_version" "db_secret_value" {
  secret_id = aws_secretsmanager_secret.db_secret.id

  secret_string = jsonencode({
    username = "appuser"
    password = "StrongPassword123!"
    dbname   = "appdb"
  })
}

