// visitor to user application functions

`
    Things to check:
    - createUserApplication: create a new user application
    - getPendingApplications: get all pending user applications to the super user
    - updateUserApplicationStatus: update the status of a user application (approve or reject)
    - changeUserRole: change the role of a user from visitor to user
    - approveUserApplication: approve a user application and change the visitor's role to user
`

import supabase from './supabaseClient';

// create a new user application
const createUserApplication = async (visitorId, arithmeticQuestion, answer) => {
    const { data, error } = await supabase
        .from('user_applications')
        .insert([
            {
                visitor_id: visitorId,
                arithmetic_question: arithmeticQuestion,
                answer: answer,
                status: 'pending',
            }
        ]);

    if (error) {
        console.error('Error creating user application:', error);
    } else {
        console.log('User application created:', data);
    }
};

// get all pending user applications
const getPendingApplications = async () => {
    const { data, error } = await supabase
        .from('user_applications')
        .select('*')
        .eq('status', 'pending');

    if (error) {
        console.error('Error fetching pending applications:', error);
    } else {
        console.log('Pending applications:', data);
        return data;
    }
};

// update the status of a user application (approve or reject)
const updateUserApplicationStatus = async (applicationId, status, superUserId = null) => {
    const updateData = {
        status: status,
    };

    // If the status is 'approved', add additional information
    if (status === 'approved') {
        updateData.approved_by = superUserId;
        updateData.approved_at = new Date();
    }

    const { data, error } = await supabase
        .from('user_applications')
        .update(updateData)
        .eq('id', applicationId);

    if (error) {
        console.error(`Error updating application status to ${status}:`, error);
    } else {
        console.log(`Application status updated to ${status}:`, data);
        return data;
    }
};

// change the role of a user from visitor to user
const changeUserRole = async (userId, newRole) => {
    const { data, error } = await supabase
        .from('users')
        .update({ role: newRole })
        .eq('id', userId);

    if (error) {
        console.error('Error changing user role:', error);
    } else {
        console.log('User role updated:', data);
        return data;
    }
};

// approve a user application and change the visitor's role to user
const approveUserApplication = async (applicationId, visitorId, superUserId) => {
    // update the application status to approved
    const approvedApplication = await updateUserApplicationStatus(applicationId, 'approved', superUserId);

    if (approvedApplication) {
        // change the user's role after successful application approval
        await changeUserRole(visitorId, 'user');
    }
};

// export functions to other parts as needed
export {
    createUserApplication,
    getPendingApplications,
    updateUserApplicationStatus,
    changeUserRole,
    approveUserApplication,
};