'use client';

import { Box, IconButton, InputBase, Typography } from '@mui/material';
import { Send } from '@mui/icons-material';
import { KeyboardEvent, useState } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
}

export function ChatInput({ onSend, disabled, isLoading }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSend = () => {
    if (value.trim() && !disabled && !isLoading) {
      onSend(value.trim());
      setValue('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 720, mx: 'auto' }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1.5,
          pl: 2.5,
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'rgba(0,0,0,0.08)',
          borderRadius: '24px',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          '&:focus-within': {
            borderColor: 'primary.main',
            boxShadow: '0 0 0 2px rgba(13, 148, 136, 0.1)',
          },
        }}
      >
        <InputBase
          fullWidth
          placeholder='Ask about your documents...'
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isLoading}
          sx={{
            fontSize: '0.975rem',
            '& input::placeholder': {
              color: 'text.secondary',
              opacity: 0.7,
            },
          }}
        />
        <IconButton
          onClick={handleSend}
          disabled={!value.trim() || disabled || isLoading}
          sx={{
            bgcolor: value.trim() ? 'primary.main' : 'grey.200',
            color: value.trim() ? 'white' : 'grey.400',
            '&:hover': {
              bgcolor: value.trim() ? 'primary.dark' : 'grey.300',
            },
            '&.Mui-disabled': {
              bgcolor: 'grey.200',
              color: 'grey.400',
            },
            transition: 'all 0.2s',
          }}
          size='small'
        >
          <Send fontSize='small' />
        </IconButton>
      </Box>
      <Typography
        variant='caption'
        color='text.secondary'
        sx={{
          mt: 1.5,
          display: 'block',
          textAlign: 'center',
          opacity: 0.7,
        }}
      >
        Your data isn&apos;t stored on our servers · AI can make mistakes
      </Typography>
    </Box>
  );
}
