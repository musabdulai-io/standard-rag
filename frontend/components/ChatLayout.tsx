'use client';

import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Description, Email, SmartToy } from '@mui/icons-material';
import { useState } from 'react';
import { ContactModal } from './ContactModal';
import { DocumentsDrawer } from './DocumentsDrawer';
import { DocumentsSidebar } from './DocumentsSidebar';
import { FloatingContactButton } from './FloatingContactButton';
import type { Document } from '@/lib/api';

interface ChatLayoutProps {
  children: React.ReactNode;
  documents: Document[];
  isLoadingDocs: boolean;
  isUploading: boolean;
  isDeletingId: string | null;
  onUpload: (files: File[]) => void;
  onDelete: (id: string) => void;
}

export function ChatLayout({
  children,
  documents,
  isLoadingDocs,
  isUploading,
  isDeletingId,
  onUpload,
  onDelete,
}: ChatLayoutProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [contactOpen, setContactOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <AppBar
        position='fixed'
        elevation={0}
        sx={{
          bgcolor: 'background.default',
          borderBottom: '1px solid',
          borderColor: 'rgba(0,0,0,0.06)',
          zIndex: theme => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', position: 'relative' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {isMobile ? (
              <Tooltip title='Standard RAG Demo'>
                <SmartToy sx={{ color: 'primary.main' }} />
              </Tooltip>
            ) : (
              <>
                <SmartToy sx={{ color: 'primary.main' }} />
                <Typography variant='h6' fontWeight={600} color='text.primary'>
                  Standard RAG Demo
                </Typography>
              </>
            )}
          </Box>

          {/* Centered Contact Button */}
          <Box
            sx={{
              position: 'absolute',
              left: '50%',
              transform: 'translateX(-50%)',
            }}
          >
            <Tooltip title='Get in touch'>
              <Box
                onClick={() => setContactOpen(true)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  px: isMobile ? 1.5 : 2,
                  py: 1,
                  borderRadius: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': { bgcolor: 'rgba(99, 102, 241, 0.1)' },
                }}
              >
                <Email sx={{ color: 'primary.main', fontSize: 20 }} />
                {!isMobile && (
                  <Typography variant='body2' fontWeight={500} color='text.primary'>
                    Get in Touch
                  </Typography>
                )}
              </Box>
            </Tooltip>
          </Box>

          {/* Right side - Only show docs toggle on mobile */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {isMobile && (
              <Tooltip title={drawerOpen ? 'Close documents' : 'View documents'}>
                <IconButton
                  onClick={() => setDrawerOpen(!drawerOpen)}
                  sx={{
                    '&:hover': { bgcolor: 'rgba(99, 102, 241, 0.1)' },
                  }}
                >
                  <Description sx={{ color: drawerOpen ? 'primary.main' : 'text.secondary' }} />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box
        sx={{
          display: 'flex',
          flex: 1,
          mt: '64px',
          overflow: 'hidden',
        }}
      >
        {/* Chat Area */}
        <Box
          sx={{
            flex: 1,
            overflow: 'hidden',
          }}
        >
          {children}
        </Box>

        {/* Desktop Sidebar - Always visible */}
        {!isMobile && (
          <DocumentsSidebar
            open={true}
            documents={documents}
            isLoading={isLoadingDocs}
            isUploading={isUploading}
            isDeletingId={isDeletingId}
            onUpload={onUpload}
            onDelete={onDelete}
          />
        )}

        {/* Mobile Drawer */}
        {isMobile && (
          <DocumentsDrawer
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            documents={documents}
            isLoading={isLoadingDocs}
            isUploading={isUploading}
            isDeletingId={isDeletingId}
            onUpload={onUpload}
            onDelete={onDelete}
          />
        )}
      </Box>

      {/* Floating Contact Button */}
      <FloatingContactButton onClick={() => setContactOpen(true)} />

      {/* Contact Modal */}
      <ContactModal open={contactOpen} onClose={() => setContactOpen(false)} />
    </Box>
  );
}
