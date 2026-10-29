import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { testService } from '../services/testService';
import { predictionService } from '../services/predictionService';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [recentTests, setRecentTests] = useState([]);
  const [hasRecommendations, setHasRecommendations] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const history = await testService.getTestHistory();
        setRecentTests(history.slice(0, 3));

        // Check if user has recommendations
        try {
          await predictionService.getRecommendations();
          setHasRecommendations(true);
        } catch (err) {
          setHasRecommendations(false);
        }
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const StatCard = ({ title, value, icon, color, action }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 48 }}>{icon}</Box>
        </Box>
      </CardContent>
      {action && (
        <CardActions>
          <Button size="small" onClick={action.onClick} endIcon={<ArrowForwardIcon />}>
            {action.label}
          </Button>
        </CardActions>
      )}
    </Card>
  );

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
        Welcome back, {user?.username}!
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Track your skill development and get personalized learning recommendations.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tests Taken"
            value={recentTests.length}
            icon={<QuizIcon />}
            color="#1976d2"
            action={{
              label: 'View History',
              onClick: () => navigate('/history'),
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Latest Score"
            value={
              recentTests.length > 0
                ? `${Math.round(recentTests[0].total_score)}%`
                : 'N/A'
            }
            icon={<TrendingUpIcon />}
            color="#2e7d32"
            action={
              hasRecommendations
                ? {
                    label: 'View Recommendations',
                    onClick: () => navigate('/recommendations'),
                  }
                : null
            }
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Learning Activities"
            value={hasRecommendations ? 'Available' : 'Take Test'}
            icon={<SchoolIcon />}
            color="#ed6c02"
            action={{
              label: hasRecommendations ? 'View' : 'Start Test',
              onClick: () =>
                hasRecommendations ? navigate('/recommendations') : navigate('/test'),
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 1 }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 1 }}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={() => navigate('/test')}
                startIcon={<QuizIcon />}
              >
                Start Random Test
              </Button>
              <Button
                variant="outlined"
                size="large"
                fullWidth
                onClick={() => navigate('/test-selection')}
                startIcon={<QuizIcon />}
              >
                Choose Topic
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Recent Test Attempts
        </Typography>
        {recentTests.length === 0 ? (
          <Card>
            <CardContent>
              <Typography color="textSecondary" align="center">
                No tests taken yet. Start by taking a test to get personalized recommendations!
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={() => navigate('/test')}
                  startIcon={<QuizIcon />}
                >
                  Take Your First Test
                </Button>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={2}>
            {recentTests.map((test) => (
              <Grid item xs={12} md={4} key={test.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Test #{test.id}
                    </Typography>
                    <Typography color="textSecondary" variant="body2" gutterBottom>
                      {new Date(test.test_date).toLocaleDateString()}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Chip
                        label={`Score: ${Math.round(test.total_score)}%`}
                        color={test.total_score >= 70 ? 'success' : test.total_score >= 50 ? 'warning' : 'error'}
                        sx={{ mr: 1 }}
                      />
                      <Chip
                        label={`${test.correct_answers}/${test.total_questions} Correct`}
                        variant="outlined"
                      />
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate(`/test-results/${test.id}`)}>
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Box>
  );
};

export default Dashboard;
