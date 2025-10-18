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
		income: '$30',
		occupation: 'walmart cashier',
		interests: ['pilates','social media','hiking']
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
	const results: EvaluationResponse[] = [];

	for (const profile of demographics) {
		try {
			const result = await callPythonAPI(apiUrl, imageBase64, profile);
			results.push(result);
		} catch (error) {
			console.error('Error evaluating for profile:', profile, error);
		}
	}

	return results;
}
