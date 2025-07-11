import React, { useEffect, useState } from 'react';
import { Typography, Box, Grid } from '@mui/material';
import { type Product } from '../types/Product';
import { useParams } from 'react-router-dom';

function ProductDetail(){

    const { id } = useParams<{ id: string }>();
    const [product, setProduct] = useState<Product | null>(null);

    useEffect(() => {
        fetch(`https://dummyjson.com/products/${id}`)
            .then(res => res.json())
            .then(data => {
                console.log("Product:", data);
                setProduct(data);
            })
            .catch(error => console.error('Error fetching product:', error));
    }, [id]);

    if (!product) {
        return <Typography>Loading...</Typography>;
    }


    return (
        <Box sx={{ padding: 2 }}>
            <Typography variant="h3">
                {product.title}
            </Typography>
            <Typography variant="h4" color="primary">
                ${product.price}
            </Typography>
            <Box sx={{ my: 2 }}>
                <img
                    src={product.images[0]}
                    alt={product.title}
                    style={{ maxWidth: '100%', height: '400px' }}
                />
            </Box>
            <Typography variant="body1" paragraph>
                {product.description}
            </Typography>
            <Typography variant="h5" sx={{ mt: 4 }}>
                Additional Images
            </Typography>
            <Grid container spacing={2}>
                {product.images.slice(1).map((image, index) => (
                    <Grid key={index}>
                        <img
                            src={image}
                            alt={`${product.title} - image ${index + 2}`}
                            style={{ width: '100%', height: 'auto' }}
                        />
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default ProductDetail;