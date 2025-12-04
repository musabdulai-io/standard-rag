'use client';

import { Box } from '@mui/material';
import { useEffect, useRef } from 'react';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { EmptyState } from './EmptyState';
import type { SearchResult } from '@/lib/api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SearchResult[];
  isLoading?: boolean;
  error?: string;
}

interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isSearching: boolean;
  hasDocuments: boolean;
}

export function ChatArea({ messages, onSendMessage, isSearching, hasDocuments }: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasMessages = messages.length > 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        minHeight: 0,
      }}
    >
      {hasMessages ? (
        <>
          {/* Messages Area */}
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 3,
              pb: 0,
            }}
          >
            <Box sx={{ maxWidth: 720, mx: 'auto' }}>
              {messages.map(message => (
                <ChatMessage
                  key={message.id}
                  role={message.role}
                  content={message.content}
                  sources={message.sources}
                  isLoading={message.isLoading}
                  error={message.error}
                />
              ))}
              <div ref={messagesEndRef} />
            </Box>
          </Box>

          {/* Sticky Input */}
          <Box
            sx={{
              px: 3,
              py: 1.5,
              bgcolor: 'background.default',
            }}
          >
            <Box sx={{ maxWidth: 720, mx: 'auto' }}>
              <ChatInput onSend={onSendMessage} isLoading={isSearching} />
            </Box>
          </Box>
        </>
      ) : (
        /* Empty State */
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <EmptyState onSuggestionClick={onSendMessage} />
          <Box sx={{ mt: 4, width: '100%' }}>
            <ChatInput onSend={onSendMessage} isLoading={isSearching} />
          </Box>
        </Box>
      )}
    </Box>
  );
}
