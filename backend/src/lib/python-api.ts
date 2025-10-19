import type { DemographicProfile, EvaluationRequest, EvaluationResponse } from '../../../shared/types';

// Default demographic profiles to use if none provided
export const DEFAULT_DEMOGRAPHICS: DemographicProfile[] = [
	{
		age: 28,
		gender: 'female',
		location: 'San Francisco',
		income: '$75k',
		occupation: 'software engineer',
		interests: ['technology', 'fitness', 'sustainability']
	},
	{
		age: 45,
		gender: 'male',
		location: 'Texas',
		income: '$55k',
		occupation: 'teacher',
		interests: ['reading', 'gardening', 'cooking']
	},
	{
		age: 35,
		gender: 'female',
		location: 'New York',
		income: '$90k',
		occupation: 'marketing manager',
		interests: ['fashion', 'travel', 'wine']
	},
	{
		age: 67,
		gender: 'male',
		location: 'Detroit',
		income: '$140k',
		occupation: 'lawyer',
		interests: ['wine','skiing','vintage cars']
	},
	{
		age: 22,
		gender: 'female',
		location: 'Michigan',
		income: '$30k',
		occupation: 'walmart cashier',
		interests: ['pilates','social media','hiking']
	},
	{
		age: 52,
		gender: 'male',
		location: 'Seattle',
		income: '$110k',
		occupation: 'architect',
		interests: ['design', 'photography', 'cycling']
	},
	{
		age: 31,
		gender: 'female',
		location: 'Austin',
		income: '$65k',
		occupation: 'graphic designer',
		interests: ['art', 'music festivals', 'food trucks']
	},
	{
		age: 58,
		gender: 'female',
		location: 'Boston',
		income: '$85k',
		occupation: 'nurse',
		interests: ['healthcare', 'knitting', 'volunteering']
	},
	{
		age: 26,
		gender: 'male',
		location: 'Los Angeles',
		income: '$48k',
		occupation: 'barista',
		interests: ['coffee', 'skateboarding', 'indie films']
	},
	{
		age: 41,
		gender: 'male',
		location: 'Chicago',
		income: '$95k',
		occupation: 'financial analyst',
		interests: ['investing', 'sports', 'craft beer']
	}
];

export async function callPythonAPI(
	apiUrl: string,
	imageBase64: string,
	demographicProfile: DemographicProfile
): Promise<EvaluationResponse> {
	const payload: EvaluationRequest = {
		image: imageBase64,
		demographic_profile: demographicProfile
	};

	const response = await fetch(apiUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(payload)
	});

	if (!response.ok) {
		const errorText = await response.text();
		console.error('Python API error response:', errorText);
		throw new Error(`Python API error: ${response.status} ${response.statusText} - ${errorText}`);
	}

	return await response.json();
}

export async function evaluateProduct(
	apiUrl: string,
	imageBase64: string,
	demographics: DemographicProfile[] = DEFAULT_DEMOGRAPHICS
): Promise<EvaluationResponse[]> {
	const promises = demographics.map(profile => 
		callPythonAPI(apiUrl, imageBase64, profile)
			.catch(error => {
				console.error('Error evaluating for profile:', profile, error);
				return null;
			})
	);

	const results = await Promise.all(promises);

	return results.filter((result): result is EvaluationResponse => result !== null);
}
