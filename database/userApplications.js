//operations for user applications table
import supabase from './supabaseClient';
const createUserApplication = async (visitorId, arithmeticQuestion, answer) =>
    {
    const { data, error } = await supabase
    .from('user_applications')
    .insert([
        { visitor_id: visitorId, arithmetic_question: arithmeticQuestion, answer: answer, status: 'pending' }]);

    if (error)
    {
        console.error('Error creating user application:', error);
    }
    else
    {
        console.log('User application created:', data);
    }
};

//add stuff for user applications table here

//switch roles from visitor to user

//user to super-user?