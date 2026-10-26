import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Grid,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { testService } from '../services/testService';

const TestResults = () => {
  const navigate = useNavigate();
  const { attemptId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(null);

  useEffect(() => {
    const fetchAttemptDetails = async () => {
      try {
        setLoading(true);
        const data = await testService.getTestAttemptDetails(attemptId);
        setAttempt(data);
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to load test results. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchAttemptDetails();
  }, [attemptId]);

  const handleViewRecommendations = () => {
    navigate('/recommendations');
  };

  const handleViewHistory = () => {
    navigate('/history');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={handleViewHistory}>
          Back to History
        </Button>
      </Box>
    );
  }

  const correctAnswers = attempt.answers.filter((a) => a.is_correct === 1);
  const wrongAnswers = attempt.answers.filter((a) => a.is_correct === 0);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Test Results
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Review your performance and see explanations for incorrect answers.
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h2" color="primary">
                  {Math.round(attempt.total_score)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Score
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h2" color="success.main">
                  {attempt.correct_answers}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Correct
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h2" color="error.main">
                  {attempt.total_questions - attempt.correct_answers}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Incorrect
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h2">
                  {Math.floor(attempt.time_taken_seconds / 60)}m
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Time Taken
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Question Review
      </Typography>

      {attempt.answers.map((answer, index) => (
        <Card key={answer.question_id} sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
              <Box sx={{ mr: 2 }}>
                {answer.is_correct === 1 ? (
                  <CheckCircleIcon sx={{ fontSize: 32, color: 'success.main' }} />
                ) : (
                  <CancelIcon sx={{ fontSize: 32, color: 'error.main' }} />
                )}
              </Box>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Question {index + 1}
                </Typography>
                <Typography variant="body1" paragraph>
                  {answer.question.question_text}
                </Typography>

                {answer.question.options && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Options:
                    </Typography>
                    {JSON.parse(answer.question.options).map((option, optIndex) => (
                      <Box
                        key={optIndex}
                        sx={{
                          p: 1,
                          mb: 0.5,
                          borderRadius: 1,
                          bgcolor:
                            option === answer.question.correct_answer
                              ? 'success.light'
                              : option === answer.user_answer && option !== answer.question.correct_answer
                              ? 'error.light'
                              : 'grey.100',
                        }}
                      >
                        <Typography variant="body2">
                          {option === answer.question.correct_answer && (
                            <strong>✓ Correct: </strong>
                          )}
                          {option === answer.user_answer && option !== answer.question.correct_answer && (
                            <strong>✗ Your Answer: </strong>
                          )}
                          {option}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}

                {!answer.question.options && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Your Answer:
                    </Typography>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        bgcolor: answer.is_correct === 1 ? 'success.light' : 'error.light',
                      }}
                    >
                      <Typography variant="body2">{answer.user_answer}</Typography>
                    </Box>
                    {answer.is_correct === 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Correct Answer:
                        </Typography>
                        <Box sx={{ p: 1, borderRadius: 1, bgcolor: 'success.light' }}>
                          <Typography variant="body2">{answer.question.correct_answer}</Typography>
                        </Box>
                      </Box>
                    )}
                  </Box>
                )}

                {answer.hint_used === 1 && (
                  <Chip label="Hint Used" size="small" color="warning" sx={{ mr: 1 }} />
                )}

                {answer.is_correct === 0 && answer.question.explanation && (
                  <Accordion sx={{ mt: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle2">View Explanation</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="textSecondary">
                        {answer.question.explanation}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      ))}

      <Divider sx={{ my: 4 }} />

      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Button
          variant="outlined"
          onClick={handleViewHistory}
          startIcon={<TrendingUpIcon />}
        >
          View History
        </Button>
        <Button
          variant="contained"
          onClick={handleViewRecommendations}
          startIcon={<SchoolIcon />}
        >
          View Recommendations
        </Button>
      </Box>
    </Box>
  );
};

export default TestResults;
