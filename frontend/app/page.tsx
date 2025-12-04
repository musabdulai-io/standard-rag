'use client';

import { useCallback, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatArea, type Message } from '@/components/ChatArea';
import { ChatLayout } from '@/components/ChatLayout';
import { deleteDocument, listDocuments, queryDocuments, uploadDocument } from '@/lib/api';

export default function Home() {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Fetch documents
  const { data: documentsData, isLoading: docsLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: listDocuments,
  });

  const documents = documentsData?.documents || [];
  const hasDocuments = documents.some(d => d.status === 'indexed');

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setDeletingId(null);
    },
    onError: () => {
      setDeletingId(null);
    },
  });

  // Query mutation (uses LLM to generate answer)
  const queryMutation = useMutation({
    mutationFn: (question: string) => queryDocuments(question),
  });

  // Handle file upload
  const handleUpload = useCallback(
    (files: File[]) => {
      files.forEach(file => {
        uploadMutation.mutate(file);
      });
    },
    [uploadMutation],
  );

  // Handle document delete
  const handleDelete = useCallback(
    (id: string) => {
      setDeletingId(id);
      deleteMutation.mutate(id);
    },
    [deleteMutation],
  );

  // Handle send message
  const handleSendMessage = useCallback(
    async (content: string) => {
      const userMessageId = `user-${Date.now()}`;
      const assistantMessageId = `assistant-${Date.now()}`;

      // Add user message
      setMessages(prev => [...prev, { id: userMessageId, role: 'user', content }]);

      // Check if documents are available
      if (!hasDocuments) {
        setMessages(prev => [
          ...prev,
          {
            id: assistantMessageId,
            role: 'assistant',
            content:
              'Please upload and index some documents first before asking questions. You can upload documents using the panel on the right.',
          },
        ]);
        return;
      }

      // Add loading assistant message
      setMessages(prev => [
        ...prev,
        { id: assistantMessageId, role: 'assistant', content: '', isLoading: true },
      ]);

      try {
        const data = await queryMutation.mutateAsync(content);

        // Update assistant message with answer and sources
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, isLoading: false, content: data.answer, sources: data.sources }
              : msg,
          ),
        );
      } catch (error: any) {
        // Update assistant message with error
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  isLoading: false,
                  error:
                    error.response?.data?.error || 'Failed to get an answer. Please try again.',
                }
              : msg,
          ),
        );
      }
    },
    [queryMutation, hasDocuments],
  );

  return (
    <ChatLayout
      documents={documents}
      isLoadingDocs={docsLoading}
      isUploading={uploadMutation.isPending}
      isDeletingId={deletingId}
      onUpload={handleUpload}
      onDelete={handleDelete}
    >
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isSearching={queryMutation.isPending}
        hasDocuments={hasDocuments}
      />
    </ChatLayout>
  );
}
