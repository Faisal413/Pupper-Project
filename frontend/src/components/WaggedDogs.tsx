import React, { useEffect, useState } from 'react';
import {
    Container, Typography, Box, Grid, Card, CardContent, CardMedia,
    Chip, CircularProgress, Alert
} from '@mui/material';
import { Pets } from '@mui/icons-material';

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

const WaggedDogs: React.FC = () => {
    const [waggedDogs, setWaggedDogs] = useState<ApiDog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    useEffect(() => {
        loadWaggedDogs();
        
        // Listen for custom event when wagged dogs are updated
        const handleWaggedDogsUpdate = () => {
            loadWaggedDogs();
        };
        
        window.addEventListener('waggedDogsUpdated', handleWaggedDogsUpdate);
        
        return () => {
            window.removeEventListener('waggedDogsUpdated', handleWaggedDogsUpdate);
        };
    }, []);

    const loadWaggedDogs = async () => {
        setLoading(true);
        setError(null);
        
        try {
            // Get all dogs
            const dogsResponse = await fetch(`${apiUrl}/dogs`);
            if (!dogsResponse.ok) {
                console.error('Dogs API error:', dogsResponse.status, dogsResponse.statusText);
                throw new Error('Failed to fetch dogs');
            }
            
            let dogsData = await dogsResponse.json();
            let allDogs = [];
            if (Array.isArray(dogsData)) {
                allDogs = dogsData;
            } else if (dogsData.dogs && Array.isArray(dogsData.dogs)) {
                allDogs = dogsData.dogs;
            } else if (dogsData.Items && Array.isArray(dogsData.Items)) {
                allDogs = dogsData.Items;
            }

            console.log('All dogs loaded:', allDogs.length);

            // Try to get interactions, but don't fail if endpoint doesn't exist
            let allInteractions = [];
            try {
                const interactionsResponse = await fetch(`${apiUrl}/interactions`);
                if (interactionsResponse.ok) {
                    let interactionsData = await interactionsResponse.json();
                    if (Array.isArray(interactionsData)) {
                        allInteractions = interactionsData;
                    } else if (interactionsData.interactions && Array.isArray(interactionsData.interactions)) {
                        allInteractions = interactionsData.interactions;
                    } else if (interactionsData.Items && Array.isArray(interactionsData.Items)) {
                        allInteractions = interactionsData.Items;
                    }
                }
            } catch (interactionError) {
                console.warn('Interactions endpoint not available:', interactionError);
            }

            console.log('All interactions loaded:', allInteractions.length);

            // Filter for wagged dogs from API
            const waggedInteractions = allInteractions.filter(
                interaction => interaction.interaction_type === 'wag' && interaction.user_id === 'current-user'
            );
            
            console.log('Wagged interactions from API:', waggedInteractions.length);
            
            let waggedDogIds = waggedInteractions.map(interaction => interaction.dog_id);
            
            // Also get wagged dogs from localStorage
            const localWaggedDogs = JSON.parse(localStorage.getItem('waggedDogs') || '[]');
            console.log('Wagged dogs from localStorage:', localWaggedDogs.length);
            
            // Combine both sources
            waggedDogIds = [...new Set([...waggedDogIds, ...localWaggedDogs])];
            
            const waggedDogsData = allDogs.filter(dog => waggedDogIds.includes(dog.dog_id));
            
            console.log('Wagged dogs found:', waggedDogsData.length);
            
            setWaggedDogs(waggedDogsData);
        } catch (err) {
            console.error('Error loading wagged dogs:', err);
            setError(`Failed to load wagged dogs: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 10, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress size={60} />
            </Container>
        );
    }

    return (
        <Container maxWidth={false} sx={{ mt: 10, mb: 4, maxWidth: '1200px', mx: 'auto', px: 2 }}>
            <Box textAlign="center" mb={6}>
                <Typography variant="h3" color="primary" gutterBottom sx={{ fontWeight: 700 }}>
                    ❤️ Your Wagged Dogs
                </Typography>
                <Typography variant="h6" color="text.secondary">
                    Dogs you've shown love to
                </Typography>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 4 }}>
                    {error}
                </Alert>
            )}

            {waggedDogs.length === 0 && !loading && !error ? (
                <Box textAlign="center" py={8}>
                    <Pets sx={{ fontSize: 80, color: 'grey.400', mb: 2 }} />
                    <Typography variant="h5" color="text.secondary" gutterBottom>
                        No wagged dogs yet
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Go back to the home page and wag some dogs!
                    </Typography>
                </Box>
            ) : (
                <Grid container spacing={3}>
                    {waggedDogs.map((dog) => (
                        <Grid item xs={12} sm={6} md={4} key={dog.dog_id}>
                            <Card sx={{ 
                                height: '100%',
                                borderRadius: 3,
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                                },
                                transition: 'all 0.3s ease'
                            }}>
                                {dog.images && dog.images.length > 0 ? (
                                    <CardMedia
                                        component="img"
                                        alt={dog.dog_name}
                                        height="200"
                                        image={dog.images[0].thumbnail_url || dog.images[0].standard_url}
                                        sx={{ objectFit: 'cover' }}
                                    />
                                ) : (
                                    <Box sx={{
                                        height: 200,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        backgroundColor: 'grey.100'
                                    }}>
                                        <Pets sx={{ fontSize: 60, color: 'grey.400' }} />
                                    </Box>
                                )}
                                
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                                        {dog.dog_name}
                                    </Typography>
                                    
                                    <Chip 
                                        label={dog.species} 
                                        color="primary" 
                                        size="small" 
                                        sx={{ mb: 2 }}
                                    />
                                    
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                        {dog.description}
                                    </Typography>
                                    
                                    <Typography variant="body2" color="text.secondary">
                                        <strong>Location:</strong> {dog.city}, {dog.state}
                                    </Typography>
                                    
                                    {dog.dog_weight && (
                                        <Typography variant="body2" color="text.secondary">
                                            <strong>Weight:</strong> {dog.dog_weight} lbs
                                        </Typography>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}
        </Container>
    );
};

export default WaggedDogs;