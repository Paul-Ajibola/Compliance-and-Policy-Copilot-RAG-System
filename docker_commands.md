my docker commands
<!-- to run the chunking -->
docker compose exec db psql -U postgres -d compliance_copilot -c "TRUNCATE documents, chunks RESTART IDENTITY CASCADE;"
docker compose exec backend python -m app.ingestion.ingest data/raw
docker compose exec db psql -U postgres -d compliance_copilot -c "SELECT COUNT(*) FROM documents; SELECT COUNT(*) FROM chunks;"


<!-- to run the embedding -->
# Rebuild image (new dependency: sentence-transformers — this one will take a while)
docker compose up -d --build

# Drop the old chunks table (all embeddings were NULL anyway — chunk text itself
# lives in Postgres but we'll regenerate it from the source files in data/raw/)
docker compose exec db psql -U postgres -d compliance_copilot -c "TRUNCATE documents, chunks RESTART IDENTITY CASCADE;"
docker compose exec db psql -U postgres -d compliance_copilot -c "DROP TABLE chunks;"

# Recreate chunks with the correct 384-dim column + HNSW index
docker compose exec backend python -m app.db.migrations

# Re-run ingestion to repopulate all 5 documents' chunks (text only, no embeddings yet)
docker compose exec backend python -m app.ingestion.ingest data/raw

# Generate embeddings for every chunk
docker compose exec backend python -m app.ingestion.embed_chunks