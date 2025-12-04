# backend/app/features/rag/services.py
"""
RAG feature business logic services.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.chunking import DocumentChunk as ChunkData
from app.core.chunking import get_chunker
from app.core.document_parser import get_parser
from app.core.embeddings import get_embedding_service
from app.core.exceptions import NotFoundError, SecurityError, ValidationError
from app.core.observability import logs
from app.core.pinecone import get_pinecone_store
from app.core.storage import get_storage
from app.features.rag.models import Document, DocumentChunk
from app.features.rag.schemas import SearchResult


class DocumentService:
    """Service for document management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(
        self,
        filename: str,
        content_type: str,
        content: bytes,
        session_id: str,
        is_sample: bool = False,
    ) -> Document:
        """Create and store a new document."""
        storage = get_storage()

        # Generate storage path
        doc_id = UUID(int=0)  # Temporary, will be replaced
        from uuid import uuid4

        doc_id = uuid4()
        storage_path = f"documents/{doc_id}/{filename}"

        # Upload to storage
        await storage.upload(storage_path, content, content_type)

        # Create document record
        document = Document(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            file_size=len(content),
            storage_path=storage_path,
            session_id=session_id,
            status="pending",
            is_sample=is_sample,
        )

        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)

        logs.info(
            f"Document created: {document.id}",
            "document_service",
            metadata={"filename": filename, "size": len(content)},
        )

        return document

    async def get_document(self, document_id: UUID) -> Document:
        """Get a document by ID."""
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise NotFoundError(f"Document not found: {document_id}")

        return document

    async def list_documents(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Document], int]:
        """List documents for a session with pagination."""
        # Get total count for this session (include sample docs)
        count_result = await self.session.execute(
            select(Document)
            .where(or_(Document.session_id == session_id, Document.is_sample == True))
            .order_by(Document.created_at.desc())
        )
        all_docs = count_result.scalars().all()
        total = len(all_docs)

        # Get paginated results (include sample docs)
        result = await self.session.execute(
            select(Document)
            .where(or_(Document.session_id == session_id, Document.is_sample == True))
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        documents = result.scalars().all()

        return list(documents), total

    async def delete_document(self, document_id: UUID, session_id: str) -> None:
        """Delete a document and its chunks. Verifies session ownership."""
        document = await self.get_document(document_id)

        # Verify session ownership (sample docs cannot be deleted via API)
        if document.session_id != session_id:
            logs.security(
                "Unauthorized delete attempt",
                "document_service",
                metadata={"document_id": str(document_id), "session_id": session_id},
            )
            raise SecurityError("You can only delete your own documents")

        # Delete from Pinecone
        pinecone = await get_pinecone_store()
        await pinecone.delete_document(document_id)

        # Delete from storage
        storage = get_storage()
        await storage.delete(document.storage_path)

        # Delete from database
        await self.session.delete(document)
        await self.session.commit()

        logs.info(f"Document deleted: {document_id}", "document_service")


class IndexingService:
    """Service for document indexing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_document(self, document_id: UUID) -> Document:
        """Index a document: parse, chunk, embed, and store in vector DB."""
        # Get document
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise NotFoundError(f"Document not found: {document_id}")

        try:
            # Update status
            document.status = "processing"
            await self.session.commit()

            # Get document content
            storage = get_storage()
            content = await storage.download(document.storage_path)

            # Parse document using Unstructured
            parser = get_parser()
            text = await parser.parse(
                content=content,
                content_type=document.content_type,
                filename=document.filename,
            )

            # Chunk the document
            chunker = get_chunker()
            chunks = chunker.chunk_text(
                text=text,
                document_id=document_id,
                metadata={"filename": document.filename},
            )

            if not chunks:
                raise ValidationError("Document produced no chunks")

            # Generate embeddings
            embedding_service = await get_embedding_service()
            texts = [chunk.text for chunk in chunks]
            embeddings = await embedding_service.embed_batch(texts)

            # Index in Pinecone
            pinecone = await get_pinecone_store()
            batch_data = [
                {
                    "chunk_id": chunk.id,
                    "document_id": document_id,
                    "embedding": embedding,
                    "metadata": {
                        "filename": document.filename,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text[:500],  # Store preview
                        "session_id": document.session_id,
                    },
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]
            await pinecone.index_chunks_batch(batch_data)

            # Store chunks in database
            for chunk in chunks:
                db_chunk = DocumentChunk(
                    id=chunk.id,
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                )
                self.session.add(db_chunk)

            # Update document status
            document.status = "indexed"
            document.chunk_count = len(chunks)
            await self.session.commit()
            await self.session.refresh(document)

            logs.info(
                f"Document indexed: {document_id}",
                "indexing_service",
                metadata={"chunks": len(chunks)},
            )

            return document

        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            await self.session.commit()

            logs.error(
                f"Failed to index document: {document_id}",
                "indexing_service",
                exception=e,
            )
            raise


class SearchService:
    """Service for semantic search."""

    async def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 10,
        score_threshold: float = 0.35,
    ) -> List[SearchResult]:
        """Search for relevant chunks."""
        # Generate query embedding
        embedding_service = await get_embedding_service()
        query_embedding = await embedding_service.embed_text(query)

        # Search Pinecone
        pinecone = await get_pinecone_store()
        results = await pinecone.search(
            query_embedding=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Format results
        search_results = []
        for chunk_id, score, metadata in results:
            search_results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    document_id=UUID(metadata.get("document_id")),
                    filename=metadata.get("filename", "unknown"),
                    text=metadata.get("text", ""),
                    score=score,
                    chunk_index=metadata.get("chunk_index", 0),
                )
            )

        logs.info(
            f"Search completed",
            "search_service",
            metadata={"query_length": len(query), "results": len(search_results)},
        )

        return search_results
