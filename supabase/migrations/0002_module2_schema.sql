-- documents table (tracks both manual uploads and Drive-synced files)
CREATE TABLE documents (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,
  storage_path        TEXT NOT NULL DEFAULT '',
  file_type           TEXT NOT NULL CHECK (file_type IN ('pdf', 'txt')),
  source              TEXT NOT NULL DEFAULT 'upload' CHECK (source IN ('upload', 'drive')),
  drive_file_id       TEXT,
  drive_modified_time TIMESTAMPTZ,
  status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'deleted')),
  error_message       TEXT,
  chunk_count         INTEGER,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER handle_updated_at BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_drive_file_id ON documents(drive_file_id) WHERE drive_file_id IS NOT NULL;

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own documents"   ON documents FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own documents" ON documents FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own documents" ON documents FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own documents" ON documents FOR DELETE USING (auth.uid() = user_id);

-- document_chunks table (1024 dims for jina-embeddings-v3)
CREATE TABLE document_chunks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id  UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  chunk_index  INTEGER NOT NULL,
  embedding    vector(1024),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);

ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own chunks"   ON document_chunks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own chunks" ON document_chunks FOR DELETE USING (auth.uid() = user_id);

-- drive_connections table (one row per connected user)
CREATE TABLE drive_connections (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  access_token   TEXT NOT NULL,
  refresh_token  TEXT NOT NULL,
  token_expiry   TIMESTAMPTZ,
  folder_id      TEXT,
  folder_name    TEXT,
  last_synced_at TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER handle_drive_updated_at BEFORE UPDATE ON drive_connections
  FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);

ALTER TABLE drive_connections ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own drive connection"   ON drive_connections FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own drive connection" ON drive_connections FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own drive connection" ON drive_connections FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own drive connection" ON drive_connections FOR DELETE USING (auth.uid() = user_id);

-- Enable Realtime on documents
ALTER PUBLICATION supabase_realtime ADD TABLE documents;
