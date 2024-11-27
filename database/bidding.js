// bidding.js
import supabase from './supabaseClient';

// will handle functions to view, place, and update bids

// view bids
const viewBids = async (listing_id) => {
    const { data, error } = await supabase
        .from('bids')
        .select('*')
        .eq('listing_id', listing_id)
        .order('amount', { ascending: false });

    if (error) {
        console.error('Error fetching bids:', error);
        return { success: false, message: 'Error fetching bids' };
    }

    console.log('Bids:', data);
    return { success: true, message: 'Bids fetched successfully', data };
}

// place a bid
const placeBid = async (listing_id, user_id, amount, deadline) =>
{
    // user should have balance to place the bid
    const { data: user, error: userError } = await supabase
        .from('users')
        .select('balance')
        .eq('id', user_id)
        .single();

    if (userError || !user)
    {
        console.error('Cannot find user:', userError);
        return { success: false, message: 'Cannot find user' };
    }

    // make sure that the user has enough balance to place the bid
    if (user.balance < amount)
    {
        return { success: false, message: 'Insufficient balance' };
    }

    // make sure the listing is not already sold
    const { data: listing, error: listingError } = await supabase
        .from('listings')
        .select('availability')
        .eq('id', listing_id)
        .single();

    if (listingError || !listing)
    {
        console.error('Cannot find listing:', listingError);
        return { success: false, message: 'Cannot find listing' };
    }

    if (listing.availability === 'sold' || listing.availability === 'rented')
    {
        return { success: false, message: 'The item is not available.' };
    }

    // check if the bid deadline has passed
    const currentTime = new Date();
    if (new Date(deadline) < currentTime)
    {
        return { success: false, message: 'Bid deadline has passed' };
    }

    // insert the bid
    const { data: bidData, error: bidError } = await supabase
        .from('bids')
        .insert([{ user_id, listing_id, amount, status: 'pending', deadline }]);

    if (bidError)
    {
        console.error('Error placing bid:', bidError);
        return { success: false, message: 'Error placing bid' };
    }

    // edit balance from user's account after placing the bid
    const updatedBalance = user.balance - amount;
    const { data: updatedUser, error: balanceError } = await supabase
        .from('users')
        .update({ balance: updatedBalance })
        .eq('id', user_id);

    if (balanceError)
    {
        console.error('Error updating balance:', balanceError);
        return { success: false, message: 'Error updating balance' };
    }

    console.log('Bid placed succesfully:', bidData);
    return { success: true, message: 'Bid placed successfully', data: bidData };
}

// accept or reject a bid (for listing owners)
const bidStatus = async (bid_id, status, listing_id, availability) =>
{
    if (!['accepted', 'rejected'].includes(status))
    {
        return { success: false, message: 'Invalid status' };
    }

    // fetch bid details
    const { data: bid, error: bidError } = await supabase
        .from('bids')
        .select('*')
        .eq('id', bid_id)
        .eq('listing_id', listing_id)
        .single();

    if (bidError || !bid)
    {
        console.error('Cannot find bid:', bidError);
        return { success: false, message: 'Cannot find bid' };
    }

    // check if current bid has expired or not
    const currentTime = new Date();

    if (new Date(bid.deadline) < currentTime)
    {
    // mark the bid as expired if the deadline has passed
    const { data: expiredBid, error: expiredBidError } = await supabase
        .from('bids')
        .update({ status: 'expired' })
        .eq('id', bid_id);

        if (expiredBidError)
        {
            console.error('Error marking bid as expired:', expiredBidError);
            return { success: false, message: 'Error updating bid status to expired' };
        }

        console.log('Bid expired:', expiredBid);
        return { success: false, message: 'This bid has expired' };
    }

    // accept or reject bid status
    const { data: updateData, error: updateError } = await supabase
        .from('bids')
        .update({ status: status })
        .eq('id', bid_id);

        if (updateError)
        {
            console.error('Error updating bid status:', updateError);
            return { success: false, message: 'Error updating bid status' };
        }

        // if bid is accepted, mark the listing as either sold or rented
        if (status === 'accepted')
        {
            // Check if availability is 'rented' or 'sold'
            const updatedAvailability = availability === 'rented' ? 'rented' : 'sold';

        const { data: listing, error: listingError } = await supabase
            .from('listings')
            .update({ availability: updatedAvailability })
            .eq('id', listing_id);

        if (listingError)
        {
            console.error('Error updating listing status:', listingError);
            return { success: false, message: 'Error updating listing status' };
        }

        // track the successful bid acceptance
        const { data: transaction, error: transactionError } = await supabase
            .from('transactions')
            .insert([
            {
                user_id: bid.user_id,
                listing_id: listing_id,
                amount: bid.amount,
                status: 'bid completed',
                created_at: new Date(),
            }]);

        if (transactionError)
        {
            console.error('Error creating transaction:', transactionError);
            return { success: false, message: 'Error creating transaction' };
        }

        console.log('Transaction created:', transaction);
    }

    return { success: true, message: `Bid ${status} successfully`, bid: updateData };
};

//delete bid
const deleteBid = async (bid_id, user_id) => {
    //fetch the bid to verify it's pending
    const { data: bid, error: bidError } = await supabase
        .from('bids')
        .select('*')
        .eq('id', bid_id)
        .eq('user_id', user_id)
        .single();

    if (bidError || !bid)
    {
        console.error('Cannot find bid:', bidError);
        return { success: false, message: 'Cannot find bid' };
    }

    if (bid.status !== 'pending')
    {
        return { success: false, message: 'Bid cannot be deleted once it is accepted or rejected' };
    }

    const { data: deletedBid, error: deleteError } = await supabase
        .from('bids')
        .delete()
        .eq('id', bid_id);

    if (deleteError)
    {
        console.error('Error deleting bid:', deleteError);
        return { success: false, message: 'Error deleting bid' };
    }

    return { success: true, message: 'Bid deleted successfully', data: deletedBid };
};

// expire bids that have passed their deadline
const expireBids = async () => {
    const currentTime = new Date();

    const { data: expiredBids, error: expiredBidError } = await supabase
        .from('bids')
        .select('*')
        .lt('deadline', currentTime.toISOString())
        .eq('status', 'pending');

    if (expiredBidError)
    {
        console.error('Error fetching expired bids:', expiredBidError);
        return { success: false, message: 'Error fetching expired bids' };
    }

    // update the expired bids status
    const { data: updatedBids, error: updateError } = await supabase
        .from('bids')
        .update({ status: 'expired' })
        .in('id', expiredBids.map(bid => bid.id));

    if (updateError)
    {
        console.error('Error updating expired bids:', updateError);
        return { success: false, message: 'Error updating expired bids' };
    }

    console.log('Expired bids marked:', updatedBids);
    return { success: true, message: 'Expired bids updated successfully', data: updatedBids };
};

export { placeBid, viewBids, bidStatus, deleteBid, expireBids};