// transactions.js

import supabase from './supabaseClient';

`
Things to do:
- deposit money into user's account
- withdraw money from user's account
- get transactions history
- edit transaction status to be 'completed'
- maybe needed: can we refund money?
`
//note - do i need to add a type to the transaction table? (deposit, withdraw, etc)

//deposit money
const deposit = async (user_id, amount) => {

    if (amount <= 0)
    {
        return {success: false, message: "Amount must be greater than 0"}
    }

    const {data: user, error: userError} = await supabase
        .from('users')
        .select('balance')
        .eq('id', user_id)
        .single();

    if (userError || !user)
    {
        console.error(userError);
        return {success: false, message: "User not found"}
    }

    const newBalance = user.balance + amount;
    const {data, error} = await supabase
        .from('users')
        .update({balance: newBalance})
        .eq('id', user_id);

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to deposit money"}
    }

    //add transaction to transactions table
    const {data: transaction, error: transactionError} = await supabase
        .from('transactions')
        .insert([
            {user_id: user_id,
                amount: amount,
                status: 'completed'}
        ]);

    if (transactionError)
    {
        console.error(transactionError);
        return {success: false, message: "Failed to add transaction"}
    }

    return {success: true, message: "Money deposited successfully"}
}

//withdraw money
const withdraw = async (user_id, amount) => {
    if (amount <= 0)
    {
        return {success: false, message: "Amount must be greater than 0"}
    }

    const {data: user, error: userError} = await supabase
        .from('users')
        .select('balance')
        .eq('id', user_id)
        .single();

    if (userError || !user)
    {
        console.error(userError);
        return {success: false, message: "User not found"}
    }

    if (user.balance < amount)
    {
        return {success: false, message: "Insufficient funds"}
    }

    const newBalance = user.balance - amount;
    const {data, error} = await supabase
        .from('users')
        .update({balance: newBalance})
        .eq('id', user_id);

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to withdraw money"}
    }

    //add transaction to transactions table
    const {data: transaction, error: transactionError} = await supabase
        .from('transactions')
        .insert([
            {user_id: user_id,
            amount: amount,
            status: 'completed'}
        ]);

    if (transactionError)
    {
        console.error(transactionError);
        return {success: false, message: "Failed to add transaction"}
    }

    return {success: true, message: "Money withdrawn successfully", data: transaction}
}

//get transactions history
const getTransactions = async (user_id) => {
    const {data: transactions, error} = await supabase
        .from('transactions')
        .select('*')
        .eq('user_id', user_id)
        .order('created_at', {ascending: false});

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to get transactions"}
    }

    return {success: true, data: transactions}
}

//edit transaction status to be 'completed', and add timestamp
const completeTransaction = async (user_id, listing_id, transaction_id, amount) => {
    const {data, error} = await supabase
        .from('transactions')
        .insert([
        {
            user_id: user_id,
            listing_id: listing_id,
            transaction_id,
            amount: amount,
            status: 'completed',
            completed_at: new Date()}
        ])

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to complete transaction"}
    }

    return {success: true, message: "Transaction completed successfully", transaction: data}
}