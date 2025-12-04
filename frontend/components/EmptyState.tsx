'use client';

import { Box, Chip, Typography } from '@mui/material';

const SUGGESTIONS = [
  'What is prompt injection?',
  'What is RAG architecture?',
  'What are LLM security risks?',
  'How does semantic search work?',
];

interface EmptyStateProps {
  onSuggestionClick?: (suggestion: string) => void;
}

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        px: 3,
      }}
    >
      <Typography variant='body1' color='text.secondary' sx={{ maxWidth: 400, mb: 3 }}>
        Upload documents to get started, then ask questions.
      </Typography>

      {/* Suggestions */}
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 1,
          justifyContent: 'center',
          maxWidth: 500,
        }}
      >
        {SUGGESTIONS.map(suggestion => (
          <Chip
            key={suggestion}
            label={suggestion}
            onClick={() => onSuggestionClick?.(suggestion)}
            sx={{
              cursor: 'pointer',
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'rgba(0,0,0,0.08)',
              '&:hover': {
                bgcolor: 'rgba(13, 148, 136, 0.08)',
                borderColor: 'primary.main',
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
}
