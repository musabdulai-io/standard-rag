'use client';

import { Box, CircularProgress, Divider, Drawer, Tooltip, Typography } from '@mui/material';
import { Lock } from '@mui/icons-material';
import { DocumentItem } from './DocumentItem';
import { UploadZone } from './UploadZone';
import type { Document } from '@/lib/api';

const SIDEBAR_WIDTH = 320;

interface DocumentsSidebarProps {
  open: boolean;
  documents: Document[];
  isLoading: boolean;
  isUploading: boolean;
  isDeletingId: string | null;
  onUpload: (files: File[]) => void;
  onDelete: (id: string) => void;
}

export function DocumentsSidebar({
  open,
  documents,
  isLoading,
  isUploading,
  isDeletingId,
  onUpload,
  onDelete,
}: DocumentsSidebarProps) {
  const indexedCount = documents.filter(d => d.status === 'indexed').length;

  return (
    <Drawer
      variant='persistent'
      anchor='right'
      open={open}
      sx={{
        width: open ? SIDEBAR_WIDTH : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: SIDEBAR_WIDTH,
          borderLeft: '1px solid',
          borderColor: 'rgba(0,0,0,0.06)',
          bgcolor: 'background.default',
          top: 64,
          height: 'calc(100% - 64px)',
        },
      }}
    >
      {/* Privacy Badge */}
      <Box sx={{ p: 2 }}>
        <Tooltip title='Stored locally in your browser' placement='left'>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1.5,
              bgcolor: 'background.paper',
              borderRadius: '12px',
              border: '1px solid',
              borderColor: 'rgba(0,0,0,0.06)',
              cursor: 'help',
            }}
          >
            <Lock sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant='body2' color='text.secondary'>
              Only you
            </Typography>
          </Box>
        </Tooltip>
      </Box>

      <Divider />

      {/* Files Section */}
      <Box sx={{ p: 2, flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <Box
          sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}
        >
          <Typography variant='subtitle2' fontWeight={600} color='text.secondary'>
            Files
          </Typography>
          <Typography variant='caption' color='text.secondary'>
            {indexedCount} / {documents.length}
          </Typography>
        </Box>

        <UploadZone onUpload={onUpload} isUploading={isUploading} />

        {/* Document List */}
        <Box
          sx={{
            mt: 2,
            flex: 1,
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
          }}
        >
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress size={24} />
            </Box>
          ) : documents.length > 0 ? (
            documents.map(doc => (
              <DocumentItem
                key={doc.id}
                document={doc}
                onDelete={onDelete}
                isDeleting={isDeletingId === doc.id}
              />
            ))
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant='body2' color='text.secondary'>
                No files uploaded
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  );
}

export { SIDEBAR_WIDTH };
