//complaints.js

import supabase from './supabaseClient';

`
Todo:
- submit a complaint
    - insert complaint into complaints table
    - complaint should have a status (pending, resolved)
- retrieve complaints (admin and users)
- resolve a complaint (admin)
- check status for a complaint (for users)
`

//submit a complaint
async function submitComplaint (complaint_user_id, defendant_id, complaint_text) {

    //check if complaint text is empty
    if (!complaint_text || complaint_text.length === 0)
    {
        return {success: false, message: "Not a valid complaint"}
    }

    //insert complaint into complaints table
    const {data: complaint, error: complaintError} = await supabase
        .from('complaints')
        .insert([
            {
                complaint_user_id: complaint_user_id,
                defendant_id: defendant_id,
                complaint_text: complaint_text,
                status: 'pending',
                created_at: new Date()
            }
        ]);

    if (complaintError)
    {
        console.error(complaintError);
        return {success: false, message: "Failed to add complaint"}
    }

    return {success: true, message: "Complaint submitted successfully", data: complaint}
}

//retrieve complaints - need to add admin check

async function getComplaints (user_id)
{
    const {data: complaints, error} = await supabase
        .from('complaints')
        .select('*')
        .eq('complaint_user_id', user_id)
        .order('created_at', {ascending: false});

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to get complaints"}
    }

    return {success: true, data: complaints}
}

//resolve a complaint - need to ensure only admin has access to this
async function resolveComplaint (complaint_id, resolution_text) {
    const {data, error} = await supabase
        .from('complaints')
        .update
        ({
            status: 'resolved',
            resolution_text: resolution_text || 'Complaint Resolved',
            resolved_at: new Date(),
        })
        .eq('id', complaint_id);

    if (error)
    {
        console.error(error);
        return {success: false, message: "Failed to resolve complaint"}
    }

    return {success: true, message: "Complaint resolved successfully"}
}

//check status for a complaint
async function checkComplaintStatus(complaint_id, user_id)
{
    const { data, error } = await supabase
        .from('complaints')
        .select('status')
        .eq('id', complaint_id)
        .eq('complainant_user_id', user_id)
        .single();

    if (error || !data)
    {
        console.error(error);
        return { success: false, message: "Complaint not found or you do not have permission to view it." };
    }

    return { success: true, status: data.status };
}

export { submitComplaint, getComplaints, resolveComplaint, checkComplaintStatus };