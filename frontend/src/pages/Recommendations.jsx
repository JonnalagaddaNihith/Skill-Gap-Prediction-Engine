import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  LinearProgress,
  Button,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  TrendingDown as TrendingDownIcon,
  School as SchoolIcon,
  Timer as TimerIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { predictionService } from '../services/predictionService';

const Recommendations = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const response = await predictionService.getRecommendations();
        setData(response);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            'No test attempts found. Please complete a test first to get recommendations.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getSeverityColor = (severity) => {
    if (severity >= 0.7) return 'error';
    if (severity >= 0.4) return 'warning';
    return 'success';
  };

  const getMasteryColor = (mastery) => {
    if (mastery >= 0.7) return 'success';
    if (mastery >= 0.4) return 'warning';
    return 'error';
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
        <Alert severity="info" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/test')}
          startIcon={<SchoolIcon />}
        >
          Take a Test
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Skill Gap Analysis & Recommendations
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Based on your test performance, here are personalized learning recommendations.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Skill Gaps" />
          <Tab label="Learning Activities" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          {data.skill_gaps.map((gap) => (
            <Grid item xs={12} md={6} key={gap.skill_id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {gap.skill_name}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        Predicted Mastery
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {Math.round(gap.predicted_mastery * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={gap.predicted_mastery * 100}
                      color={getMasteryColor(gap.predicted_mastery)}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        Gap Severity
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {Math.round(gap.gap_severity * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={gap.gap_severity * 100}
                      color={getSeverityColor(gap.gap_severity)}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Box>
                  {gap.observed_accuracy !== null && (
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Observed Accuracy: {Math.round(gap.observed_accuracy * 100)}%
                    </Typography>
                  )}
                  {gap.n_attempts !== null && (
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Attempts: {gap.n_attempts}
                    </Typography>
                  )}
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Weak Areas
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                    {gap.weak_difficulties.map((diff, index) => (
                      <Chip
                        key={index}
                        label={diff}
                        size="small"
                        color="warning"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {gap.weak_problem_types.map((type, index) => (
                      <Chip
                        key={index}
                        label={type}
                        size="small"
                        color="error"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          {data.recommendations.map((activity) => (
            <Grid item xs={12} md={6} lg={4} key={activity.activity_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Chip
                      label={activity.type}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      label={activity.difficulty}
                      size="small"
                      color={
                        activity.difficulty === 'easy'
                          ? 'success'
                          : activity.difficulty === 'medium'
                          ? 'warning'
                          : 'error'
                      }
                    />
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {activity.title}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TimerIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="textSecondary">
                      {activity.duration_min} minutes
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StarIcon sx={{ fontSize: 16, mr: 1, color: 'warning.main' }} />
                    <Typography variant="body2" color="textSecondary">
                      Relevance: {Math.round(activity.relevance_score * 100)}%
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Matched Skills
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {activity.matched_skills.map((skill, index) => (
                      <Chip key={index} label={skill} size="small" variant="outlined" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          onClick={() => navigate('/test')}
          startIcon={<SchoolIcon />}
        >
          Take Another Test
        </Button>
      </Box>
    </Box>
  );
};

export default Recommendations;
