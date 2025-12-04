'use client';

import { useState } from 'react';
import { Box, Chip, Collapse, IconButton, LinearProgress, Typography } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import type { SearchResult } from '@/lib/api';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: SearchResult[];
  isLoading?: boolean;
  error?: string;
}

export function ChatMessage({ role, content, sources, isLoading, error }: ChatMessageProps) {
  const isUser = role === 'user';
  const [sourcesExpanded, setSourcesExpanded] = useState(true);

  // User message - gray background, black text, all corners rounded, no avatar
  if (isUser) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        <Box
          sx={{
            bgcolor: 'grey.200',
            color: 'text.primary',
            borderRadius: '16px',
            p: 2,
            maxWidth: '80%',
          }}
        >
          <Typography variant='body1'>{content}</Typography>
        </Box>
      </Box>
    );
  }

  // Assistant message - no background, no avatar, inherits container background
  return (
    <Box sx={{ mb: 3, maxWidth: '85%' }}>
      {isLoading ? (
        <Box>
          <Typography variant='body2' color='text.secondary' sx={{ mb: 1 }}>
            Thinking...
          </Typography>
          <LinearProgress sx={{ borderRadius: 1, maxWidth: 200 }} />
        </Box>
      ) : error ? (
        <Typography variant='body1' color='error.main'>
          {error}
        </Typography>
      ) : content ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Answer text */}
          <Typography variant='body1' sx={{ lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {content}
          </Typography>

          {/* Sources section */}
          {sources && sources.length > 0 && (
            <Box>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer',
                  color: 'text.secondary',
                  '&:hover': { color: 'text.primary' },
                }}
                onClick={() => setSourcesExpanded(!sourcesExpanded)}
              >
                <Typography variant='body2' fontWeight={500}>
                  {sources.length} source{sources.length !== 1 ? 's' : ''}
                </Typography>
                <IconButton size='small' sx={{ ml: 0.5 }}>
                  {sourcesExpanded ? (
                    <ExpandLessIcon fontSize='small' />
                  ) : (
                    <ExpandMoreIcon fontSize='small' />
                  )}
                </IconButton>
              </Box>

              <Collapse in={sourcesExpanded}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mt: 1.5 }}>
                  {sources.map(source => (
                    <Box
                      key={source.chunk_id}
                      sx={{
                        p: 2,
                        border: '1px solid',
                        borderColor: 'rgba(0,0,0,0.08)',
                        borderRadius: '12px',
                        bgcolor: 'grey.50',
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          mb: 1,
                        }}
                      >
                        <Typography variant='subtitle2' fontWeight={600}>
                          {source.filename}
                        </Typography>
                        <Chip
                          size='small'
                          label={`${(source.score * 100).toFixed(0)}%`}
                          color='primary'
                          sx={{ height: 22, fontSize: '0.7rem' }}
                        />
                      </Box>
                      <Typography variant='body2' color='text.secondary' sx={{ lineHeight: 1.6 }}>
                        {source.text}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Collapse>
            </Box>
          )}
        </Box>
      ) : (
        <Typography variant='body1' color='text.secondary'>
          No relevant results found. Try uploading more documents or rephrasing your question.
        </Typography>
      )}
    </Box>
  );
}
