import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon, Quiz as QuizIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const TestSelection = () => {
  const navigate = useNavigate();
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');

  // Available skills (should match backend SKILLS)
  const skills = [
    { id: 'SK001', name: 'Python Basics' },
    { id: 'SK002', name: 'Python Loops' },
    { id: 'SK003', name: 'Functions' },
    { id: 'SK004', name: 'Data Structures' },
    { id: 'SK005', name: 'SQL Queries' },
    { id: 'SK006', name: 'SQL Joins' },
    { id: 'SK007', name: 'Debugging' },
    { id: 'SK008', name: 'Algorithms' },
  ];

  const difficulties = ['Easy', 'Medium', 'Hard'];

  const handleStartTest = () => {
    const params = new URLSearchParams();
    if (selectedSkill) params.append('skill_id', selectedSkill);
    if (selectedDifficulty) params.append('difficulty', selectedDifficulty);

    navigate(`/test?${params.toString()}`);
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          variant="outlined"
          onClick={handleBack}
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h4">Choose Your Test Topic</Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Skill
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Choose a skill to focus on</InputLabel>
                <Select
                  value={selectedSkill}
                  label="Choose a skill to focus on"
                  onChange={(e) => setSelectedSkill(e.target.value)}
                >
                  <MenuItem value="">
                    <em>All Skills (Random)</em>
                  </MenuItem>
                  {skills.map((skill) => (
                    <MenuItem key={skill.id} value={skill.id}>
                      {skill.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Leave empty to get questions from all skills
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Difficulty
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Choose difficulty level</InputLabel>
                <Select
                  value={selectedDifficulty}
                  label="Choose difficulty level"
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                >
                  <MenuItem value="">
                    <em>All Difficulties (Random)</em>
                  </MenuItem>
                  {difficulties.map((diff) => (
                    <MenuItem key={diff} value={diff}>
                      {diff}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Leave empty to get questions of all difficulties
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Ready to Start?
                  </Typography>
                  <Typography variant="body2">
                    {selectedSkill && selectedDifficulty
                      ? `You selected: ${skills.find(s => s.id === selectedSkill)?.name} - ${selectedDifficulty}`
                      : selectedSkill
                      ? `You selected: ${skills.find(s => s.id === selectedSkill)?.name} (All difficulties)`
                      : selectedDifficulty
                      ? `You selected: ${selectedDifficulty} (All skills)`
                      : 'Random test with questions from all skills and difficulties'}
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleStartTest}
                  startIcon={<QuizIcon />}
                  sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: 'grey.100' } }}
                >
                  Start Test
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Skills
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {skills.map((skill) => (
                  <Chip
                    key={skill.id}
                    label={skill.name}
                    onClick={() => setSelectedSkill(skill.id)}
                    sx={{
                      cursor: 'pointer',
                      bgcolor: selectedSkill === skill.id ? 'primary.main' : 'default',
                      color: selectedSkill === skill.id ? 'white' : 'text.primary',
                    }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TestSelection;
