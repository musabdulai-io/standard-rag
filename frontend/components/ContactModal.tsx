'use client';

import { Box, Dialog, DialogContent, DialogTitle, IconButton, Typography } from '@mui/material';
import { CalendarMonth, Close, Email } from '@mui/icons-material';

interface ContactModalProps {
  open: boolean;
  onClose: () => void;
}

const CONTACT_EMAIL = 'hello@musabdulai.com';
const BOOKING_URL = 'https://calendly.com/musabdulai/ai-security-check';

export function ContactModal({ open, onClose }: ContactModalProps) {
  const handleEmail = () => {
    window.location.href = `mailto:${CONTACT_EMAIL}`;
    onClose();
  };

  const handleBookCall = () => {
    window.open(BOOKING_URL, '_blank', 'noopener,noreferrer');
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth='xs'
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '16px',
          bgcolor: 'background.default',
        },
      }}
    >
      <DialogTitle
        sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}
      >
        <Typography variant='h6' fontWeight={600}>
          Get in Touch
        </Typography>
        <IconButton onClick={onClose} size='small'>
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent sx={{ pb: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Email Option */}
          <Box
            onClick={handleEmail}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: 2,
              borderRadius: '12px',
              border: '1px solid',
              borderColor: 'rgba(0,0,0,0.08)',
              cursor: 'pointer',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: 'rgba(13, 148, 136, 0.05)',
                borderColor: 'primary.main',
              },
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: '10px',
                bgcolor: 'rgba(13, 148, 136, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Email sx={{ color: 'primary.main' }} />
            </Box>
            <Box>
              <Typography variant='subtitle1' fontWeight={600}>
                Send an Email
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                {CONTACT_EMAIL}
              </Typography>
            </Box>
          </Box>

          {/* Book a Call Option */}
          <Box
            onClick={handleBookCall}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: 2,
              borderRadius: '12px',
              border: '1px solid',
              borderColor: 'rgba(0,0,0,0.08)',
              cursor: 'pointer',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: 'rgba(13, 148, 136, 0.05)',
                borderColor: 'primary.main',
              },
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: '10px',
                bgcolor: 'rgba(13, 148, 136, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CalendarMonth sx={{ color: 'primary.main' }} />
            </Box>
            <Box>
              <Typography variant='subtitle1' fontWeight={600}>
                Book a Call
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Schedule a meeting
              </Typography>
            </Box>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
