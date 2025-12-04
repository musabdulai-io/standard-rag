'use client';

import { Fab, Tooltip, keyframes } from '@mui/material';
import { Email } from '@mui/icons-material';

const wiggle = keyframes`
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-8deg); }
  50% { transform: rotate(0deg); }
  75% { transform: rotate(8deg); }
`;

interface FloatingContactButtonProps {
  onClick: () => void;
}

export function FloatingContactButton({ onClick }: FloatingContactButtonProps) {
  return (
    <Tooltip title='Get in touch' placement='left'>
      <Fab
        onClick={onClick}
        size='medium'
        sx={{
          position: 'fixed',
          bottom: { xs: 140, md: 120 },
          left: { xs: 'auto', md: 24 },
          right: { xs: 24, md: 'auto' },
          display: 'flex',
          bgcolor: 'primary.main',
          color: 'white',
          zIndex: 1000,
          '&:hover': {
            bgcolor: 'primary.dark',
          },
          '& .MuiSvgIcon-root': {
            animation: `${wiggle} 1s ease-in-out infinite`,
            animationDelay: '2s',
            animationIterationCount: 3,
          },
          '@keyframes pulse': {
            '0%': { boxShadow: '0 0 0 0 rgba(13, 148, 136, 0.4)' },
            '70%': { boxShadow: '0 0 0 10px rgba(13, 148, 136, 0)' },
            '100%': { boxShadow: '0 0 0 0 rgba(13, 148, 136, 0)' },
          },
          animation: 'pulse 2s infinite',
        }}
      >
        <Email />
      </Fab>
    </Tooltip>
  );
}
