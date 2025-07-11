import React, { useState } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, Button, Grid, Alert, CircularProgress, Box, Typography
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

interface AddDogProps {
    open: boolean;
    onClose: () => void;
    onDogAdded: () => void;
}

const AddDog: React.FC<AddDogProps> = ({ open, onClose, onDogAdded }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        shelter: '',
        city: '',
        state: '',
        dog_name: '',
        species: 'Labrador Retriever',
        description: '',
        dog_weight: '',
        dog_color: ''
    });
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const apiUrl = import.meta.env.VITE_API_URL;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            let s3Key = null;
            
            // Step 1: Upload image if selected
            if (selectedImage) {
                console.log('🖼️ Starting image upload for:', selectedImage.name);
                
                // Get presigned URL
                const presignedResponse = await fetch(`${apiUrl}/upload/presigned`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        filename: selectedImage.name,
                        file_size: selectedImage.size,
                        content_type: selectedImage.type
                    })
                });
                
                console.log('📡 Presigned response status:', presignedResponse.status);
                
                if (!presignedResponse.ok) {
                    const errorText = await presignedResponse.text();
                    console.error('❌ Presigned URL error:', errorText);
                    throw new Error(`Failed to get presigned URL: ${errorText}`);
                }
                
                const presignedData = await presignedResponse.json();
                console.log('📡 Presigned data:', presignedData);
                
                // Upload to S3 using presigned URL
                const s3Response = await fetch(presignedData.upload_url, {
                    method: 'PUT',
                    body: selectedImage,
                    headers: {
                        'Content-Type': selectedImage.type
                    }
                });
                
                console.log('☁️ S3 response status:', s3Response.status);
                
                if (!s3Response.ok) {
                    const s3ErrorText = await s3Response.text();
                    console.error('❌ S3 upload error:', s3ErrorText);
                    throw new Error(`Failed to upload image to S3: ${s3ErrorText}`);
                }
                
                s3Key = presignedData.s3_key;
                console.log('✅ Image uploaded to S3:', s3Key);
            }

            // Step 2: Complete dog registration
            const dogData = {
                shelter: formData.shelter,
                city: formData.city,
                state: formData.state,
                dog_name: formData.dog_name,
                dog_species: formData.species,
                dog_description: formData.description,
                dog_weight: formData.dog_weight,
                dog_color: formData.dog_color
            };
            
            if (s3Key) {
                dogData.s3_key = s3Key;
            }

            const endpoint = s3Key ? `${apiUrl}/upload/complete` : `${apiUrl}/dogs`;
            console.log('🐕 Calling endpoint:', endpoint);
            console.log('🐕 Dog data:', dogData);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dogData)
            });

            console.log('🐕 Registration response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Registration error:', errorText);
                throw new Error(`Failed to add dog: ${errorText}`);
            }
            
            const result = await response.json();
            console.log('✅ Dog registered:', result);
            
            onDogAdded();
            onClose();
            setFormData({
                shelter: '',
                city: '',
                state: '',
                dog_name: '',
                species: 'Labrador Retriever',
                description: '',
                dog_weight: '',
                dog_color: ''
            });
            setSelectedImage(null);
            setImagePreview(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to add dog');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [field]: e.target.value }));
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Add New Dog for Adoption</DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    
                    <Grid container spacing={2}>
                        {/* Image Upload */}
                        <Grid item xs={12}>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    Dog Photo
                                </Typography>
                                <input
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                    id="image-upload"
                                    type="file"
                                    onChange={handleImageChange}
                                />
                                <label htmlFor="image-upload">
                                    <Button
                                        variant="outlined"
                                        component="span"
                                        startIcon={<CloudUpload />}
                                        fullWidth
                                    >
                                        Upload Dog Photo
                                    </Button>
                                </label>
                                {imagePreview && (
                                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                                        <img
                                            src={imagePreview}
                                            alt="Preview"
                                            style={{
                                                maxWidth: '200px',
                                                maxHeight: '200px',
                                                borderRadius: '8px'
                                            }}
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            {selectedImage?.name}
                                        </Typography>
                                    </Box>
                                )}
                            </Box>
                        </Grid>
                        
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Dog Name"
                                value={formData.dog_name}
                                onChange={handleChange('dog_name')}
                                required
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Species (Must be Labrador Retriever)"
                                value={formData.species}
                                onChange={handleChange('species')}
                                helperText="Only Labrador Retrievers are accepted"
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
                                placeholder="e.g., 65 or sixty-five pounds"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Color"
                                value={formData.dog_color}
                                onChange={handleChange('dog_color')}
                                placeholder="e.g., Golden, Chocolate, Black"
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
                        {loading ? 'Adding...' : 'Add Dog'}
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
};

export default AddDog;