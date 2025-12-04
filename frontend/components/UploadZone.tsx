'use client';

import { Box, LinearProgress, Tooltip, Typography } from '@mui/material';
import { Add } from '@mui/icons-material';
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface UploadZoneProps {
  onUpload: (files: File[]) => void;
  isUploading?: boolean;
}

export function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles);
      }
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
    },
    disabled: isUploading,
  });

  return (
    <Box>
      <Tooltip title='Drag & drop .txt, .md, or .pdf files' placement='top'>
        <Box
          {...getRootProps()}
          sx={{
            p: 2,
            border: '1px dashed',
            borderColor: isDragActive ? 'primary.main' : 'rgba(0,0,0,0.12)',
            borderRadius: '12px',
            bgcolor: isDragActive ? 'rgba(13, 148, 136, 0.05)' : 'transparent',
            cursor: isUploading ? 'default' : 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'rgba(13, 148, 136, 0.03)',
            },
          }}
        >
          <input {...getInputProps()} />
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
            }}
          >
            <Add
              sx={{
                fontSize: 20,
                color: isDragActive ? 'primary.main' : 'text.secondary',
              }}
            />
            <Typography variant='body2' color={isDragActive ? 'primary.main' : 'text.secondary'}>
              {isDragActive ? 'Drop files here' : 'Add files'}
            </Typography>
          </Box>
          <Typography variant='caption' color='text.secondary' sx={{ display: 'block', mt: 0.5 }}>
            .txt, .md, .pdf
          </Typography>
        </Box>
      </Tooltip>
      {isUploading && <LinearProgress sx={{ mt: 1, borderRadius: 1 }} />}
    </Box>
  );
}
