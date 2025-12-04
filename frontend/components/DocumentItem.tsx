'use client';

import { Box, Chip, IconButton, Tooltip, Typography } from '@mui/material';
import { Close, Description } from '@mui/icons-material';
import type { Document } from '@/lib/api';

interface DocumentItemProps {
  document: Document;
  onDelete: (id: string) => void;
  isDeleting?: boolean;
}

export function DocumentItem({ document, onDelete, isDeleting }: DocumentItemProps) {
  const getFileExtension = (filename: string) => {
    const ext = filename.split('.').pop()?.toUpperCase() || 'FILE';
    return ext;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'indexed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 1.5,
        p: 1.5,
        bgcolor: '#f8f7f5',
        borderRadius: '12px',
        transition: 'background-color 0.15s',
        '&:hover': {
          bgcolor: '#f0efed',
        },
      }}
    >
      <Box
        sx={{
          width: 36,
          height: 36,
          borderRadius: '8px',
          bgcolor: 'rgba(13, 148, 136, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Description sx={{ fontSize: 18, color: 'primary.main' }} />
      </Box>

      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography
          variant='body2'
          fontWeight={500}
          sx={{
            wordBreak: 'break-word',
            lineHeight: 1.3,
            mb: 0.5,
          }}
        >
          {document.filename}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {document.status === 'indexed' && (
            <Typography variant='caption' color='text.secondary'>
              {document.chunk_count} chunks
            </Typography>
          )}
          <Chip
            size='small'
            label={getFileExtension(document.filename)}
            sx={{
              height: 18,
              fontSize: '0.65rem',
              fontWeight: 600,
              bgcolor: 'rgba(0,0,0,0.06)',
              color: 'text.secondary',
            }}
          />
          {document.is_sample && (
            <Chip
              size='small'
              label='Sample'
              sx={{
                height: 18,
                fontSize: '0.65rem',
                fontWeight: 600,
                bgcolor: 'rgba(0,0,0,0.06)',
                color: 'text.secondary',
              }}
            />
          )}
          {document.status !== 'indexed' && (
            <Chip
              size='small'
              label={document.status}
              color={getStatusColor(document.status) as any}
              sx={{ height: 18, fontSize: '0.65rem' }}
            />
          )}
        </Box>
      </Box>

      <Tooltip title='Remove document'>
        <IconButton
          size='small'
          onClick={() => onDelete(document.id)}
          disabled={isDeleting}
          sx={{
            opacity: 0.5,
            '&:hover': { opacity: 1, color: 'error.main' },
          }}
        >
          <Close fontSize='small' />
        </IconButton>
      </Tooltip>
    </Box>
  );
}
