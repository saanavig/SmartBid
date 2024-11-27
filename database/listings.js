import supabase from './supabaseClient';

// will handle creating new listings, updating listings, and deleting listings
// also will check if the listing is 'for-sale', 'for-rent', 'sold', or 'rented'

const createListing = async (user_id, title, description, price, availability) => {
    // check if the item is available or not
    const validAvailability = ['for-sale', 'for-rent'];
    if (!validAvailability.includes(availability))
    {
        return { success: false, message: 'Item is not available for sale or rent'};
    }

    // ensure that the price is a positive number
    if (price <= 0)
    {
        return { success: false, message: 'Please add a valid price for the item.' };
    }

    // create the listing
    const { data, error } = await supabase
        .from('listings')
        .insert([
            {
                user_id: user_id,
                title: title,
                description: description,
                price: price,
                availability: availability,
            }
        ]);

    if (error)
    {
        console.error('Error creating listing:', error);
        return { success: false, message: 'Error creating listing' };
    }

    console.log('Listing Successful:', data);
    return { success: true, message: 'Listing created successfully', data };
}

//update listing details and mark as sold or rented, if needed
const updateListing = async (listing_id, user_id, title, description, price, availability) => 
{
    //get current listings
    const {data: listing, error: listingError} = await supabase
        .from('listings')
        .select('*')
        .eq('id', listing_id)
        .eq('user_id', user_id)
        .single();

        if (listingError || !listing)
        {
            console.error('Error fetching listing:', listingError);
            return { success: false, message: 'Cannot find the listing' };
        }

        //check if the listing is sold or rented
        if (listing.availability === 'sold' || listing.availability === 'rented')
        {
            return { success: false, message: 'Listing is already sold or rented' };
        }

        // ensure that the price is a positive number
        if (price <= 0)
        {
            return { success: false, message: 'Please add a valid price for the item.' };
        }

        const validAvailability = ['for-sale', 'for-rent'];
        if (!validAvailability.includes(availability))
        {
            return { success: false, message: 'Item is not available for sale, or rent.' };
        }

        //update the listing
        const {data, error} = await supabase
        .from
        .update({
            title: title,
            description: description,
            price: price,
            availability: availability,
        })
        .eq('id', listing_id);

        if (error)
        {
            console.error('Error updating listing:', error);
            return { success: false, message: 'Error updating listing' };
        }

        console.log('Listing updated:', data);
        return { success: true, message: 'Listing updated successfully', data };
}

//delete a listing
const deleteListing = async (listing_id, user_id) =>
{
    //get current listings
    const {data: listing, error: listingError} = await supabase
        .from('listings')
        .select('*')
        .eq('id', listing_id)
        .eq('user_id', user_id)
        .single();

        if (listingError || !listing)
        {
            console.error('Error fetching listing:', listingError);
            return { success: false, message: 'Cannot find the listing' };
        }

        if (listing.availability === 'sold' || listing.availability === 'rented')
        {
            return { success: false, message: 'Cannot delete a listing that is sold or rented.' };
        }

        //delete the listing
        const {data, error} = await supabase
        .from('listings')
        .delete()
        .eq('id', listing_id);

        if (error)
        {
            console.error('Error deleting listing:', error);
            return { success: false, message: 'Error deleting listing' };
        }

        console.log('Listing deleted:', data);
        return { success: true, message: 'Listing deleted successfully', data };
}

//ensure the role of the item is marked as sold or rented as needed
const SoldOrRented = async (listing_id, status) => {
    const validStatus = ['sold', 'rented'];
    if (!validStatus.includes(status))
    {
        return { success: false, message: 'Invalid status' };
    }

    //update the listing
    const {data, error} = await supabase
    .from('listings')
    .update({
        availability: status,
    })
    .eq('id', listing_id);

    if (error)
    {
        console.error('Error updating listing:', error);
        return { success: false, message: 'Error updating listing' };
    }

    console.log('Listing marked as', status, ':', data);
    return { success: true, message: `Listing marked as ${status}.`, data };
}

//fetch all listings
const getListing = async () =>
    {
        const {data, error} = await supabase
        .from('listings')
        .select('*')
        .eq('availability', availability)
        .order('created_at', {ascending: false});
        if (error)
        {
            console.error('Error fetching listings:', error);
            return { success: false, message: error.message };
        }
        else
        {
            console.log('Listings:', data);
            return { success: true, data };
        }
    }


export {createListing, updateListing, deleteListing, SoldOrRented, getListing };