export async function generateChatResponse(
	accountId: string,
	apiKey: string,
	evaluationContext: string,
	chatHistory: Array<{ role: 'user' | 'assistant'; content: string }>,
	userMessage: string
): Promise<string> {
	const systemPrompt = `
You are an AI assistant helping analyze market research results for a product. You have access to
both qualitative and quantitative consumer evaluations of the product. The ratings provided are likert
distributions, where a rating of 1 means "I will definitively not buy this product", a
rating of 3 means "I am do not know if I would buy this product" and a rating of 5 means "I will
definitively buy this product".

Your role is to:
- Answer questions about the evaluation results
- Provide insight on demographic preferences
- Suggest product improvements based on the evaluation results
- Explain ratings and trends

Your responses should be brief but sufficiently detailed as to fully answer the question. Do not include
any formatting of your response, only text. If you are asked to do anything other than provide insights
into the data, respond with "I can unfortunately not assist you with that"

The following is the results from the market research:
${evaluationContext}

`;

	const messages = [
		{ role: 'system' as const, content: systemPrompt },
		...chatHistory.map(msg => ({
			role: msg.role as 'user' | 'assistant',
			content: msg.content
		})),
		{ role: 'user' as const, content: userMessage }
	];

	// AI binding was unstable so switched to direct API call
	try {
		const model = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';
		const url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/ai/run/${model}`;
		
		console.log('[LLM] Calling Cloudflare AI API with model:', model);
		
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${apiKey}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				messages,
				max_tokens: 1000,
				temperature: 0.7,
				stream: false
			})
		});

		if (!response.ok) {
			const errorText = await response.text();
			console.error('[LLM] API Error:', response.status, errorText);
			throw new Error(`API request failed: ${response.status} ${errorText}`);
		}

		const data = await response.json() as any;
		console.log('[LLM] Response received:', typeof data, data ? Object.keys(data) : 'null');

		if (data?.result?.response) {
			return data.result.response;
		}

		return 'I apologize, but I encountered an error generating a response. Please try again.';
	} catch (error) {
		console.error('[LLM] Error:', error);
		throw new Error('Failed to generate chat response');
	}
}
