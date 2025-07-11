export interface Dog {
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