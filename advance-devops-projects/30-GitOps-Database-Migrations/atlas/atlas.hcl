env "prod" {
  url = env("DB_URL")
  migration {
    dir = "file://migrations"
  }
}
