import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Avatar,
  Button,
  Divider,
  Grid,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Manage your account settings and view your profile information.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  margin: '0 auto',
                  bgcolor: 'primary.main',
                  fontSize: 48,
                }}
              >
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
              <Typography variant="h5" sx={{ mt: 2 }}>
                {user?.username}
              </Typography>
              <Chip
                label="Active User"
                color="success"
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Information
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PersonIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Username
                      </Typography>
                      <Typography variant="body1">{user?.username}</Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CalendarIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Member Since
                      </Typography>
                      <Typography variant="body1">
                        {user?.created_at
                          ? new Date(user.created_at).toLocaleDateString()
                          : 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <EmailIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        User ID
                      </Typography>
                      <Typography variant="body1">#{user?.id}</Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Account Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  disabled
                >
                  Edit Profile (Coming Soon)
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                About Skill Gap Prediction
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                This platform uses machine learning to analyze your test performance and provide
                personalized learning recommendations. Take tests to identify your skill gaps and
                receive tailored learning activities to improve your proficiency.
              </Typography>
              <Typography variant="body2" color="textSecondary">
                <strong>Features:</strong>
              </Typography>
              <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                <li>
                  <Typography variant="body2" color="textSecondary">
                    Interactive skill assessment tests
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" color="textSecondary">
                    AI-powered skill gap analysis
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" color="textSecondary">
                    Personalized learning recommendations
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" color="textSecondary">
                    Track your progress over time
                  </Typography>
                </li>
              </ul>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;
