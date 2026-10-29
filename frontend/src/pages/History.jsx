import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Grid,
} from '@mui/material';
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { testService } from '../services/testService';

const History = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const data = await testService.getTestHistory();
        setHistory(data);
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to load test history. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const handleRefresh = () => {
    window.location.reload();
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'success';
    if (score >= 50) return 'warning';
    return 'error';
  };

  const formatTime = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Test History</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={handleRefresh}
            startIcon={<RefreshIcon />}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/test')}
            startIcon={<TrendingUpIcon />}
          >
            Take New Test
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {history.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="textSecondary" align="center" variant="h6" gutterBottom>
              No test history found
            </Typography>
            <Typography color="textSecondary" align="center" paragraph>
              You haven't taken any tests yet. Start by taking a test to track your progress!
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                onClick={() => navigate('/test')}
                startIcon={<TrendingUpIcon />}
              >
                Take Your First Test
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Test ID</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Score</TableCell>
                <TableCell>Correct</TableCell>
                <TableCell>Total Questions</TableCell>
                <TableCell>Time Taken</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((attempt) => (
                <TableRow key={attempt.id} hover>
                  <TableCell>#{attempt.id}</TableCell>
                  <TableCell>
                    {new Date(attempt.test_date).toLocaleDateString()}{' '}
                    {new Date(attempt.test_date).toLocaleTimeString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${Math.round(attempt.total_score)}%`}
                      color={getScoreColor(attempt.total_score)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{attempt.correct_answers}</TableCell>
                  <TableCell>{attempt.total_questions}</TableCell>
                  <TableCell>{formatTime(attempt.time_taken_seconds)}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => navigate(`/test-results/${attempt.id}`)}
                    >
                      View Analysis
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {history.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Performance Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Tests
                  </Typography>
                  <Typography variant="h4">{history.length}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Average Score
                  </Typography>
                  <Typography variant="h4">
                    {Math.round(
                      history.reduce((sum, h) => sum + h.total_score, 0) / history.length
                    )}
                    %
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Best Score
                  </Typography>
                  <Typography variant="h4">
                    {Math.round(Math.max(...history.map((h) => h.total_score)))}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Questions
                  </Typography>
                  <Typography variant="h4">
                    {history.reduce((sum, h) => sum + h.total_questions, 0)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default History;
