import React, { useEffect, useState } from 'react';
import {
    Card, CardContent, CardMedia, Typography, Grid, Container, Box,
    TextField, Button, Chip, CircularProgress, Alert, IconButton,
    FormControl, InputLabel, Select, MenuItem, Paper, Divider
} from '@mui/material';
import { Favorite, ThumbDown, Search, FilterList, Pets, Edit } from '@mui/icons-material';
import { type Dog } from '../types/Dog';
import EditDog from './EditDog';

interface ApiDog {
    dog_id: string;
    shelter_id: string;
    dog_name: string;
    species: string;
    description: string;
    shelter: string;
    city: string;
    state: string;
    dog_weight?: number;
    dog_color?: string;
    images?: Array<{
        thumbnail_url: string;
        original_url: string;
        standard_url: string;
    }>;
}

function Home() {
    const [dogs, setDogs] = useState<ApiDog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [stateFilter, setStateFilter] = useState('');
    const [colorFilter, setColorFilter] = useState('');
    const [interactions, setInteractions] = useState<{[key: string]: string}>({});
    const [editDogOpen, setEditDogOpen] = useState(false);
    const [editingDogId, setEditingDogId] = useState<string | null>(null);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        loadDogs();
    }, []);

    const loadDogs = async () => {
        setLoading(true);
        setError(null);
        
        console.log('=== STARTING API CALL ===');
        console.log('API URL:', apiUrl);
        console.log('Full URL:', `${apiUrl}/dogs`);
        console.log('Environment VITE_API_URL:', import.meta.env.VITE_API_URL);
        
        try {
            const response = await fetch(`${apiUrl}/dogs`);
            
            console.log('=== FETCH COMPLETED ===');
            console.log('Response received:', response);
            console.log('Response status:', response.status);
            console.log('Response statusText:', response.statusText);
            console.log('Response ok:', response.ok);
            
            if (!response.ok) {
                console.log('Response not OK, getting error text...');
                const errorText = await response.text();
                console.log('Error response body:', errorText);
                setError(`API Error ${response.status}: ${errorText}`);
                return;
            }
            
            console.log('Getting JSON data...');
            const data = await response.json();
            console.log('=== API RESPONSE DATA ===');
            console.log('Raw data:', data);
            console.log('Data type:', typeof data);
            
            if (data && typeof data === 'object') {
                console.log('Data keys:', Object.keys(data));
            }
            
            // Handle different response structures
            let dogsArray = [];
            if (Array.isArray(data)) {
                dogsArray = data;
            } else if (data.dogs && Array.isArray(data.dogs)) {
                dogsArray = data.dogs;
            } else if (data.Items && Array.isArray(data.Items)) {
                dogsArray = data.Items;
            }
            
            console.log('Final dogs array:', dogsArray);
            console.log('Dogs count:', dogsArray.length);
            
            // Debug: Check if any dogs have images
            dogsArray.forEach((dog, index) => {
                console.log(`🐕 Dog ${index}:`, {
                    name: dog.dog_name,
                    hasImages: !!dog.images,
                    imageCount: dog.images ? dog.images.length : 0,
                    imageUrls: dog.images ? dog.images.map(img => img.thumbnail_url) : [],
                    fullImageData: dog.images
                });
            });
            
            setDogs(dogsArray);
            
            if (dogsArray.length === 0) {
                setError('No dogs found in database. Use the + button or "Add Test Dog" to create sample data!');
            }
            
        } catch (fetchError) {
            console.log('=== FETCH ERROR ===');
            console.log('Error object:', fetchError);
            console.log('Error name:', fetchError.name);
            console.log('Error message:', fetchError.message);
            console.log('Error stack:', fetchError.stack);
            
            // Check for specific error types
            if (fetchError.name === 'TypeError') {
                setError('Network Error: Cannot reach the API. Check your internet connection and API URL.');
            } else if (fetchError.message.includes('CORS')) {
                setError('CORS Error: API is not configured to accept requests from this domain.');
            } else {
                setError('API Server Error (500): There\'s an issue with the backend. Try adding a test dog first!');
            }
        } finally {
            setLoading(false);
        }
    };

    const addTestDog = async () => {
        try {
            const testDog = {
                shelter: "Happy Paws Shelter",
                city: "Seattle",
                state: "WA",
                dog_name: "Buddy",
                species: "Labrador Retriever",
                description: "Friendly and energetic dog looking for a loving home",
                dog_weight: "65",
                dog_color: "Golden"
            };
            
            console.log('Adding test dog to:', `${apiUrl}/dogs`);
            console.log('Test dog data:', testDog);
            
            const response = await fetch(`${apiUrl}/dogs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testDog)
            });
            
            console.log('Add dog response status:', response.status);
            console.log('Add dog response ok:', response.ok);
            
            const result = await response.json();
            console.log('Add dog full response:', result);
            
            if (response.ok) {
                setError(null);
                loadDogs(); // Reload dogs
            } else {
                setError(`Failed to add test dog: ${result.error || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('Error adding test dog:', err);
            setError(`Error adding test dog: ${err.message}`);
        }
    };

    const handleWagGrowl = async (dogId: string, shelterId: string, type: 'wag' | 'growl') => {
        // Update UI immediately
        setInteractions(prev => ({ ...prev, [dogId]: type }));
        
        // Save to localStorage
        const savedInteractions = JSON.parse(localStorage.getItem('waggedDogs') || '[]');
        if (type === 'wag') {
            if (!savedInteractions.includes(dogId)) {
                savedInteractions.push(dogId);
                localStorage.setItem('waggedDogs', JSON.stringify(savedInteractions));
            }
        } else {
            const index = savedInteractions.indexOf(dogId);
            if (index > -1) {
                savedInteractions.splice(index, 1);
                localStorage.setItem('waggedDogs', JSON.stringify(savedInteractions));
            }
        }
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('waggedDogsUpdated'));
        
        // Try API call (optional)
        try {
            await fetch(`${apiUrl}/interactions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: 'current-user',
                    shelter_id: shelterId,
                    dog_id: dogId,
                    interaction_type: type
                })
            });
        } catch (error) {
            console.error('Error recording interaction to API:', error);
        }
    };

    const handleImageClick = (imageUrl: string) => {
        if (imageUrl) {
            window.open(imageUrl, '_blank');
        }
    };

    const filteredDogs = dogs.filter(dog => {
        const matchesSearch = dog.dog_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             dog.description?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesState = !stateFilter || dog.state === stateFilter;
        const matchesColor = !colorFilter || dog.dog_color?.toLowerCase().includes(colorFilter.toLowerCase());
        
        return matchesSearch && matchesState && matchesColor;
    });

    const uniqueStates = [...new Set(dogs.map(dog => dog.state).filter(Boolean))];
    const uniqueColors = [...new Set(dogs.map(dog => dog.dog_color).filter(Boolean))];

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 10, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress size={60} />
            </Container>
        );
    }

    return (
        <Box sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%)',
            minHeight: '100vh',
            position: 'relative',
            '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(255,255,255,0.9)',
                zIndex: 1
            }
        }}>
        <Container maxWidth="xl" sx={{ 
            mt: { xs: '80px', sm: '90px', md: '100px' }, 
            mb: 8,
            px: { xs: 2, sm: 3, md: 4, lg: 6 },
            position: 'relative',
            zIndex: 2
        }}>
            {/* Header */}
            <Box textAlign="center" mb={8} sx={{ py: { xs: 4, md: 6 } }}>
                <Typography variant="h2" component="h1" gutterBottom sx={{ 
                    fontWeight: 800,
                    fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4rem' },
                    color: '#232F3E',
                    mb: 3
                }}>
                    🐕 Find Your Perfect Companion
                </Typography>
                <Typography variant="h5" sx={{ 
                    fontWeight: 300,
                    maxWidth: '600px',
                    mx: 'auto',
                    lineHeight: 1.4,
                    fontSize: { xs: '1.1rem', sm: '1.3rem' },
                    color: '#666',
                    mb: 4
                }}>
                    Discover loving Labrador Retrievers waiting for their forever homes
                </Typography>
            </Box>

            {/* Search and Filters */}
            <Paper elevation={0} sx={{ 
                p: { xs: 4, sm: 5, md: 6 }, 
                mb: 8,
                background: 'rgba(255,255,255,0.95)',
                backdropFilter: 'blur(30px)',
                border: '2px solid rgba(255,255,255,0.8)',
                borderRadius: 6,
                boxShadow: '0 20px 60px rgba(102,126,234,0.15), 0 8px 32px rgba(0,0,0,0.1)',
                maxWidth: '1400px',
                mx: 'auto',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '4px',
                    background: 'linear-gradient(90deg, #667eea, #764ba2, #f093fb)',
                    zIndex: 1
                }
            }}>
                <Grid container spacing={{ xs: 3, sm: 4, md: 5 }} alignItems="stretch">
                    <Grid item xs={12} lg={5}>
                        <TextField
                            fullWidth
                            variant="outlined"
                            placeholder="Search for your perfect companion..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            sx={{
                                height: '100%',
                                '& .MuiOutlinedInput-root': {
                                    height: { xs: '56px', sm: '64px' },
                                    borderRadius: 3,
                                    background: 'rgba(255,255,255,0.9)',
                                    backdropFilter: 'blur(10px)',
                                    border: '2px solid transparent',
                                    fontSize: { xs: '1rem', sm: '1.1rem' },
                                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                    '&:hover': {
                                        background: 'rgba(255,255,255,1)',
                                        transform: 'translateY(-2px)',
                                        boxShadow: '0 8px 25px rgba(0,0,0,0.1)'
                                    },
                                    '&.Mui-focused': {
                                        background: 'rgba(255,255,255,1)',
                                        border: '2px solid #667eea',
                                        transform: 'translateY(-2px)',
                                        boxShadow: '0 12px 35px rgba(102,126,234,0.2)'
                                    }
                                }
                            }}
                            InputProps={{
                                startAdornment: (
                                    <Search sx={{ 
                                        mr: 2, 
                                        fontSize: { xs: '1.3rem', sm: '1.5rem' },
                                        color: searchTerm ? '#667eea' : 'text.secondary',
                                        transition: 'all 0.3s ease',
                                        transform: searchTerm ? 'scale(1.1)' : 'scale(1)'
                                    }} />
                                )
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} lg={2.5}>
                        <FormControl fullWidth sx={{
                            '& .MuiOutlinedInput-root': {
                                height: { xs: '56px', sm: '64px' },
                                borderRadius: 3,
                                background: 'rgba(255,255,255,0.9)',
                                backdropFilter: 'blur(10px)',
                                fontSize: { xs: '1rem', sm: '1.1rem' },
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                '&:hover': {
                                    background: 'rgba(255,255,255,1)',
                                    transform: 'translateY(-1px)',
                                    boxShadow: '0 4px 15px rgba(0,0,0,0.08)'
                                },
                                '&.Mui-focused': {
                                    background: 'rgba(255,255,255,1)',
                                    transform: 'translateY(-1px)',
                                    boxShadow: '0 8px 25px rgba(0,0,0,0.1)'
                                }
                            },
                            '& .MuiInputLabel-root': {
                                fontSize: { xs: '1rem', sm: '1.1rem' },
                                fontWeight: 500
                            }
                        }}>
                            <InputLabel>Filter by State</InputLabel>
                            <Select
                                value={stateFilter}
                                label="Filter by State"
                                onChange={(e) => setStateFilter(e.target.value)}
                                MenuProps={{
                                    PaperProps: {
                                        sx: {
                                            borderRadius: 2,
                                            mt: 1,
                                            boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
                                        }
                                    }
                                }}
                            >
                                <MenuItem value="" sx={{ fontSize: { xs: '1rem', sm: '1.1rem' } }}>All States</MenuItem>
                                {uniqueStates.map(state => (
                                    <MenuItem key={state} value={state} sx={{ fontSize: { xs: '1rem', sm: '1.1rem' } }}>{state}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6} lg={2.5}>
                        <FormControl fullWidth sx={{
                            '& .MuiOutlinedInput-root': {
                                height: { xs: '56px', sm: '64px' },
                                borderRadius: 3,
                                background: 'rgba(255,255,255,0.9)',
                                backdropFilter: 'blur(10px)',
                                fontSize: { xs: '1rem', sm: '1.1rem' },
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                '&:hover': {
                                    background: 'rgba(255,255,255,1)',
                                    transform: 'translateY(-1px)',
                                    boxShadow: '0 4px 15px rgba(0,0,0,0.08)'
                                },
                                '&.Mui-focused': {
                                    background: 'rgba(255,255,255,1)',
                                    transform: 'translateY(-1px)',
                                    boxShadow: '0 8px 25px rgba(0,0,0,0.1)'
                                }
                            },
                            '& .MuiInputLabel-root': {
                                fontSize: { xs: '1rem', sm: '1.1rem' },
                                fontWeight: 500
                            }
                        }}>
                            <InputLabel>Filter by Color</InputLabel>
                            <Select
                                value={colorFilter}
                                label="Filter by Color"
                                onChange={(e) => setColorFilter(e.target.value)}
                                MenuProps={{
                                    PaperProps: {
                                        sx: {
                                            borderRadius: 2,
                                            mt: 1,
                                            boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
                                        }
                                    }
                                }}
                            >
                                <MenuItem value="" sx={{ fontSize: { xs: '1rem', sm: '1.1rem' } }}>All Colors</MenuItem>
                                {uniqueColors.map(color => (
                                    <MenuItem key={color} value={color} sx={{ fontSize: { xs: '1rem', sm: '1.1rem' } }}>{color}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} lg={2.5} sx={{ display: 'flex', alignItems: 'stretch' }}>
                        <Button
                            fullWidth
                            variant="outlined"
                            size="large"
                            onClick={() => {
                                setSearchTerm('');
                                setStateFilter('');
                                setColorFilter('');
                            }}
                            startIcon={<FilterList sx={{ fontSize: { xs: '1.2rem', sm: '1.4rem' } }} />}
                            sx={{
                                height: { xs: '56px', sm: '64px' },
                                borderRadius: 3,
                                background: 'rgba(255,255,255,0.9)',
                                backdropFilter: 'blur(10px)',
                                border: '2px solid rgba(226,232,240,0.8)',
                                color: 'text.primary',
                                fontWeight: 600,
                                fontSize: { xs: '1rem', sm: '1.1rem' },
                                minWidth: { xs: '140px', sm: '160px', md: '180px' },
                                px: { xs: 2, sm: 3, md: 4 },
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                '&:hover': {
                                    background: 'linear-gradient(45deg, #667eea, #764ba2)',
                                    color: 'white',
                                    border: '2px solid transparent',
                                    transform: 'translateY(-2px)',
                                    boxShadow: '0 8px 25px rgba(102,126,234,0.3)'
                                }
                            }}
                        >
                            Clear Filters
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {/* Error Message */}
            {error && (
                <Alert severity="warning" sx={{ mb: 4 }} action={
                    <Box>
                        <Button color="inherit" size="small" onClick={loadDogs} sx={{ mr: 1 }}>
                            Retry
                        </Button>
                        <Button color="inherit" size="small" onClick={addTestDog}>
                            Add Test Dog
                        </Button>
                    </Box>
                }>
                    {error}
                </Alert>
            )}

            {/* Dogs Grid */}
            <Grid container spacing={3}>
                {filteredDogs.map((dog) => (
                    <Grid item xs={12} sm={6} lg={4} key={dog.dog_id}>
                        <Card sx={{ 
                            height: '100%',
                            borderRadius: 2,
                            border: '1px solid #e0e0e0',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-4px)',
                                boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
                            }
                        }}>
                            {/* Dog Image */}
                            {dog.images && dog.images.length > 0 ? (
                                <CardMedia
                                    component="img"
                                    alt={dog.dog_name}
                                    height="240"
                                    image={dog.images[0].thumbnail_url || dog.images[0].standard_url}
                                    sx={{ objectFit: 'cover' }}
                                />
                            ) : (
                                <Box sx={{
                                    height: 240,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    backgroundColor: '#f5f5f5',
                                    color: '#999'
                                }}>
                                    <Pets sx={{ fontSize: 60 }} />
                                </Box>
                            )}
                            
                            <CardContent sx={{ p: 3 }}>
                                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 1 }}>
                                    {dog.dog_name}
                                </Typography>
                                
                                <Chip 
                                    label={dog.species} 
                                    size="small" 
                                    sx={{ mb: 2, backgroundColor: '#e3f2fd' }}
                                />
                                
                                <Typography variant="body2" sx={{ mb: 2, color: '#666', lineHeight: 1.5 }}>
                                    {dog.description}
                                </Typography>
                                
                                <Box sx={{ mb: 2, '& > *': { mb: 0.5 } }}>
                                    <Typography variant="body2" sx={{ color: '#333' }}>
                                        <Box component="span" sx={{ fontWeight: 600 }}>Shelter:</Box> {dog.shelter}
                                    </Typography>
                                    <Typography variant="body2" sx={{ color: '#333' }}>
                                        <Box component="span" sx={{ fontWeight: 600 }}>Location:</Box> {dog.city}, {dog.state}
                                    </Typography>
                                    {dog.dog_weight && (
                                        <Typography variant="body2" sx={{ color: '#333' }}>
                                            <Box component="span" sx={{ fontWeight: 600 }}>Weight:</Box> {dog.dog_weight} lbs
                                        </Typography>
                                    )}
                                    {dog.dog_color && (
                                        <Typography variant="body2" sx={{ color: '#333' }}>
                                            <Box component="span" sx={{ fontWeight: 600 }}>Color:</Box> {dog.dog_color}
                                        </Typography>
                                    )}
                                </Box>
                                
                                <Box sx={{ borderTop: '1px solid #e0e0e0', pt: 2, mt: 2 }} />
                                
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Button
                                        variant={interactions[dog.dog_id] === 'wag' ? 'contained' : 'outlined'}
                                        startIcon={<Favorite />}
                                        onClick={() => handleWagGrowl(dog.dog_id, dog.shelter_id, 'wag')}
                                        sx={{
                                            backgroundColor: interactions[dog.dog_id] === 'wag' ? '#FF9900' : 'transparent',
                                            borderColor: '#FF9900',
                                            color: interactions[dog.dog_id] === 'wag' ? 'white' : '#FF9900',
                                            '&:hover': {
                                                backgroundColor: '#FF9900',
                                                color: 'white'
                                            }
                                        }}
                                    >
                                        Wag ♥
                                    </Button>
                                    
                                    <IconButton
                                        onClick={() => {
                                            setEditingDogId(dog.dog_id);
                                            setEditDogOpen(true);
                                        }}
                                        sx={{ color: '#666' }}
                                    >
                                        <Edit />
                                    </IconButton>
                                    
                                    <IconButton
                                        onClick={() => handleWagGrowl(dog.dog_id, dog.shelter_id, 'growl')}
                                        sx={{ color: '#666' }}
                                    >
                                        <ThumbDown />
                                    </IconButton>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            
            {/* No Results */}
            {filteredDogs.length === 0 && !loading && !error && (
                <Box textAlign="center" py={12} sx={{ maxWidth: '500px', mx: 'auto' }}>
                    <Pets sx={{ fontSize: 100, color: 'grey.400', mb: 3 }} />
                    <Typography variant="h5" color="text.secondary" sx={{ mb: 2, fontWeight: 500 }}>
                        No dogs match your search criteria
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                        Try adjusting your filters or search terms
                    </Typography>
                    <Button 
                        variant="contained" 
                        size="large"
                        onClick={() => {
                            setSearchTerm('');
                            setStateFilter('');
                            setColorFilter('');
                        }}
                        sx={{ 
                            borderRadius: 3,
                            px: 4,
                            py: 1.5
                        }}
                    >
                        Clear All Filters
                    </Button>
                </Box>
            )}
            
            {/* Edit Dog Dialog */}
            {editingDogId && (
                <EditDog
                    open={editDogOpen}
                    onClose={() => {
                        setEditDogOpen(false);
                        setEditingDogId(null);
                    }}
                    onDogUpdated={() => {
                        loadDogs();
                        setEditDogOpen(false);
                        setEditingDogId(null);
                    }}
                    dogId={editingDogId}
                />
            )}
        </Container>
        </Box>
    );
}

export default Home;