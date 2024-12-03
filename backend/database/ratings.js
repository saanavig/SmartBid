//ratings.js

import supabase from './supabaseClient';

`
Todo:
- submit a rating when there is a succesful transaction
    - make sure that one user is rating only once
    - insert rating into ratings table
    - rating should be between 1 and 5
- retrieve ratings
- get average rating of a user (for suspending users)
`
//submit a rating
async function submitRating(user_id, rated_user_id, transaction_id, rating, comment) {

    // Check if rating is between 1 and 5
    if (rating < 1 || rating > 5)
    {
        return { success: false, message: "Rating must be between 1 and 5" };
    }

    // Check if the transaction is completed
    const { data: transactionData, error: transactionError } = await supabase
        .from('transactions')
        .select('status')
        .eq('id', transaction_id)
        .single();

    if (transactionError || transactionData.status !== 'completed')
    {
        return { success: false, message: "Transaction must be completed before rating" };
    }

    // Ensure the user hasn't already rated this transaction
    const { data: ratingExists, error: ratingExistsError } = await supabase
        .from('ratings')
        .select('id')
        .eq('transaction_id', transaction_id)
        .eq('user_id', user_id)
        .single();

    if (ratingExists)
    {
        return { success: false, message: "You have already rated this transaction" };
    }

    // Insert the new rating into the ratings table
    const { data: ratingData, error: ratingError } = await supabase
        .from('ratings')
        .insert([
        {
            user_id: user_id,
            rated_user_id: rated_user_id,
            transaction_id: transaction_id,
            rating: rating,
            comment: comment,
            created_at: new Date(),
        }
        ]);

    if (ratingError)
    {
        console.error(ratingError);
        return { success: false, message: "Failed to submit rating" };
    }

    return { success: true, message: "Rating submitted successfully" };
}

//fetch ratings
async function getRatingsForUser(rated_user_id)
{
    const { data: ratings, error } = await supabase
        .from('ratings')
        .select('rating, comment, created_at, user_id')
        .eq('rated_user_id', rated_user_id)
        .order('created_at', { ascending: false });

    if (error)
    {
        console.error(error);
        return { success: false, message: "Failed to retrieve ratings" };
    }

    return { success: true, ratings };
}

//find average ratings
async function getAverageRating(rated_user_id)
{
    const { data, error } = await supabase
        .from('ratings')
        .select('rating')
        .eq('rated_user_id', rated_user_id);

    if (error)
    {
        console.error(error);
        return { success: false, message: "Failed to calculate average rating" };
    }

    // Calculate average rating
    const averageRating = data.reduce((acc, { rating }) => acc + rating, 0) / data.length;

    return { success: true, average_rating: averageRating.toFixed(2) };
}

export { submitRating, getRatingsForUser, getAverageRating };