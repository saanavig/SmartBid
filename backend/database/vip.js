//vip.js

import supabase from './supabaseClient';

`
Todo:
- check if a user qualifies for VIP status
    - more than 5k in account
    - more than 5 successful transactions
    - no complaints
- grant VIP status
- VIP suspension - back to U
`

const VIPEligible = async (userId) => {

    // check for balance
    const { data: userData, error: userError } = await supabase
        .from('users')
        .select('balance')
        .eq('id', userId)
        .single();

    if (userError)
    {
        console.error('Error fetching user balance:', userError);
        return { success: false, message: 'Error fetching user balance' };
    }

    if (userData.balance <= 5000)
    {
        return { success: false, message: 'User does not have enough balance for VIP status.' };
    }

    //5 successful transactions
    const { data: transactions, error: transactionsError } = await supabase
        .from('transactions')
        .select('*')
        .eq('user_id', userId)
        .eq('status', 'completed');

    if (transactionsError)
    {
        console.error('Error fetching transactions:', transactionsError);
        return { success: false, message: 'Error fetching transactions' };
    }

    if (transactions.length <= 5)
    {
        return { success: false, message: 'User does not have enough transactions.' };
    }

    //no complaints
    const { data: complaints, error: complaintsError } = await supabase
        .from('complaints')
        .select('*')
        .or(`complainant_user_id.eq.${userId},defendant_user_id.eq.${userId}`);

    if (complaintsError)
    {
        console.error('Error fetching complaints:', complaintsError);
        return { success: false, message: 'Error fetching complaints' };
    }

    if (complaints.length > 0)
    {
        return { success: false, message: 'User has complaints and cannot be VIP.' };
    }

    return { success: true, message: 'User qualifies for VIP status.' };
};

// Grant VIP status to a user
const grantVIP = async (userId, reason = 'Met VIP criteria') => {
    // Check if user already has VIP status
    const { data: existingVIP, error: existingVIPError } = await supabase
        .from('vip_status')
        .select('*')
        .eq('user_id', userId)
        .eq('status', 'active')
        .single();

    if (existingVIP)
    {
        return { success: false, message: 'User already has active VIP status.' };
    }

    //insert new VIP status record
    const { data, error } = await supabase
        .from('vip_status')
        .insert([
            {
                user_id: userId,
                start_date: new Date(),
                reason: reason,
                status: 'active',
            },
        ]);

    if (error)
    {
        console.error('Error granting VIP status:', error);
        return { success: false, message: 'Failed to grant VIP status.' };
    }

    return { success: true, message: 'VIP status granted successfully!' };
};

// Suspend VIP status for a user
const VIPSuspension = async (userId) => {

    const { data: expiredVIP, error: expiredVIPError } = await supabase
        .from('vip_status')
        .update({ status: 'expired' })
        .eq('user_id', userId)
        .eq('status', 'active');

    if (expiredVIPError)
    {
        console.error('Error downgrading VIP status:', expiredVIPError);
        return { success: false, message: 'Error downgrading VIP status.' };
    }

    const { data: userRoleData, error: userRoleError } = await supabase
        .from('users')
        .update({ role: 'user' })
        .eq('id', userId);

    if (userRoleError)
    {
        console.error('Error updating user role:', userRoleError);
        return { success: false, message: 'Error updating user role.' };
    }

    return { success: true, message: 'User downgraded to ordinary user.' };
};

export { VIPEligible, grantVIP, VIPSuspension };