import React, { useState, useEffect } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, Button, Grid, Alert, CircularProgress
} from '@mui/material';

interface EditDogProps {
    open: boolean;
    onClose: () => void;
    onDogUpdated: () => void;
    dogId: string;
}

const EditDog: React.FC<EditDogProps> = ({ open, onClose, onDogUpdated, dogId }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        shelter: '',
        city: '',
        state: '',
        dog_name: '',
        description: '',
        dog_weight: '',
        dog_color: ''
    });

    const apiUrl = import.meta.env.VITE_API_URL;

    useEffect(() => {
        if (open && dogId) {
            loadDogData();
        }
    }, [open, dogId]);

    const loadDogData = async () => {
        try {
            const response = await fetch(`${apiUrl}/dogs`);
            const data = await response.json();
            const dog = data.dogs?.find((d: any) => d.dog_id === dogId);
            
            if (dog) {
                setFormData({
                    shelter: dog.shelter || '',
                    city: dog.city || '',
                    state: dog.state || '',
                    dog_name: dog.dog_name || '',
                    description: dog.description || '',
                    dog_weight: dog.dog_weight || '',
                    dog_color: dog.dog_color || ''
                });
            }
        } catch (err) {
            setError('Failed to load dog data');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${apiUrl}/dogs/${dogId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update dog');
            }

            onDogUpdated();
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update dog');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [field]: e.target.value }));
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Edit Dog Information</DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Dog Name"
                                value={formData.dog_name}
                                onChange={handleChange('dog_name')}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Description"
                                value={formData.description}
                                onChange={handleChange('description')}
                                multiline
                                rows={3}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Shelter Name"
                                value={formData.shelter}
                                onChange={handleChange('shelter')}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                fullWidth
                                label="City"
                                value={formData.city}
                                onChange={handleChange('city')}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                fullWidth
                                label="State"
                                value={formData.state}
                                onChange={handleChange('state')}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Weight (lbs)"
                                value={formData.dog_weight}
                                onChange={handleChange('dog_weight')}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Color"
                                value={formData.dog_color}
                                onChange={handleChange('dog_color')}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose} disabled={loading}>
                        Cancel
                    </Button>
                    <Button 
                        type="submit" 
                        variant="contained" 
                        disabled={loading}
                        startIcon={loading ? <CircularProgress size={20} /> : null}
                    >
                        {loading ? 'Updating...' : 'Update Dog'}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
};

export default EditDog;