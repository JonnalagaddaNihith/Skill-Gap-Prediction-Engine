import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  TextField,
  CircularProgress,
  Alert,
  Chip,
  Collapse,
} from '@mui/material';
import { ArrowBack, ArrowForward, Lightbulb as LightbulbIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { testService } from '../services/testService';

const Test = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [hintsShown, setHintsShown] = useState({});
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const data = await testService.getQuestions({ numQuestions: 10 });
        setQuestions(data);
        setStartTime(Date.now());
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to load questions. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  const handleAnswerChange = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });
  };

  const handleShowHint = (questionId) => {
    setHintsShown({
      ...hintsShown,
      [questionId]: true,
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      setError('Please answer all questions before submitting.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const timeTaken = Math.floor((Date.now() - startTime) / 1000);
      const testData = {
        time_taken_seconds: timeTaken,
        answers: questions.map((q) => ({
          question_id: q.id,
          user_answer: answers[q.id] || '',
          time_taken_seconds: null,
          hint_used: hintsShown[q.id] ? 1 : 0,
          attempt_number: 1,
        })),
      };

      const result = await testService.submitTest(testData);
      navigate(`/test-results/${result.id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to submit test. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Skill Assessment Test
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Answer all questions to get personalized learning recommendations.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Question {currentQuestionIndex + 1} of {questions.length}
        </Typography>
        <Box
          sx={{
            height: 8,
            bgcolor: 'grey.200',
            borderRadius: 4,
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              height: '100%',
              bgcolor: 'primary.main',
              width: `${progress}%`,
              transition: 'width 0.3s ease',
            }}
          />
        </Box>
      </Box>

      {currentQuestion && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ mb: 2 }}>
              <Chip
                label={currentQuestion.skill_name}
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip
                label={currentQuestion.difficulty}
                size="small"
                color={
                  currentQuestion.difficulty === 'easy'
                    ? 'success'
                    : currentQuestion.difficulty === 'medium'
                    ? 'warning'
                    : 'error'
                }
              />
            </Box>
            <Typography variant="h6" gutterBottom>
              {currentQuestion.question_text}
            </Typography>

            {currentQuestion.options ? (
              <FormControl component="fieldset" sx={{ mt: 2 }}>
                <RadioGroup
                  value={answers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                >
                  {JSON.parse(currentQuestion.options).map((option, index) => (
                    <FormControlLabel
                      key={index}
                      value={option}
                      control={<Radio />}
                      label={option}
                    />
                  ))}
                </RadioGroup>
              </FormControl>
            ) : (
              <TextField
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                placeholder="Type your answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                sx={{ mt: 2 }}
              />
            )}

            {currentQuestion.hints && (
              <Box sx={{ mt: 2 }}>
                {!hintsShown[currentQuestion.id] ? (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleShowHint(currentQuestion.id)}
                    startIcon={<LightbulbIcon />}
                  >
                    Show Hint
                  </Button>
                ) : (
                  <Alert severity="info" sx={{ mt: 1 }}>
                    <Typography variant="body2">
                      <strong>Hint:</strong> {currentQuestion.hints}
                    </Typography>
                  </Alert>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          variant="outlined"
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          startIcon={<ArrowBack />}
        >
          Previous
        </Button>
        <Box>
          {currentQuestionIndex === questions.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting}
              color="success"
            >
              {submitting ? 'Submitting...' : 'Submit Test'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
              endIcon={<ArrowForward />}
            >
              Next
            </Button>
          )}
        </Box>
      </Box>

      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Question Navigation
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {questions.map((q, index) => (
            <Button
              key={q.id}
              variant={currentQuestionIndex === index ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setCurrentQuestionIndex(index)}
              sx={{
                minWidth: 40,
                bgcolor: answers[q.id] ? 'success.light' : undefined,
              }}
            >
              {index + 1}
            </Button>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default Test;
