import type { Ai } from '@cloudflare/workers-types';

export async function generateChatResponse(
	ai: Ai,
	evaluationContext: string,
	chatHistory: Array<{ role: 'user' | 'assistant'; content: string }>,
	userMessage: string
): Promise<string> {
	const systemPrompt = `
You are an AI assistant helping analyze market research results for a product. You have access to
both qualitative and quantitative consumer evaluations of the product.

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

	try {
		const response = await ai.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
			messages,
			max_tokens: 1000,
			temperature: 0.7,
			stream: false
		});

		if (response && typeof response === 'object' && 'response' in response) {
			return (response as any).response;
		}

		return 'I apologize, but I encountered an error generating a response. Please try again.';
	} catch (error) {
		console.error('LLM error:', error);
		throw new Error('Failed to generate chat response');
	}
}
