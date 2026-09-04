my docker commands
docker compose exec db psql -U postgres -d compliance_copilot -c "TRUNCATE documents, chunks RESTART IDENTITY CASCADE;"
docker compose exec backend python -m app.ingestion.ingest data/raw
docker compose exec db psql -U postgres -d compliance_copilot -c "SELECT COUNT(*) FROM documents; SELECT COUNT(*) FROM chunks;"