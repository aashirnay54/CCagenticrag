CREATE OR REPLACE FUNCTION match_document_chunks(
  query_embedding  vector(1024),
  match_user_id    UUID,
  match_count      INT DEFAULT 5,
  match_threshold  FLOAT DEFAULT 0.7
)
RETURNS TABLE (
  id UUID, document_id UUID, document_name TEXT,
  chunk_index INT, content TEXT, distance FLOAT
)
LANGUAGE SQL STABLE AS $$
  SELECT dc.id, dc.document_id, d.name AS document_name,
         dc.chunk_index, dc.content, (dc.embedding <=> query_embedding) AS distance
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  WHERE dc.user_id = match_user_id
    AND d.status = 'completed'
    AND (dc.embedding <=> query_embedding) < match_threshold
  ORDER BY distance ASC
  LIMIT match_count;
$$;
