import { SessionObject } from './durable-objects/SessionObject';
import { evaluateProduct } from './lib/python-api';
import { generateChatResponse } from './lib/llm';
import type { CreateSessionRequest, ChatRequest } from '../../shared/types';

export { SessionObject };

interface Env {
	SESSIONS: DurableObjectNamespace;
	AI: any;
	PYTHON_API_URL: string;
	CLOUDFLARE_ACCOUNT_ID: string;
	CLOUDFLARE_API_KEY: string;
	ENVIRONMENT?: string;
}


const corsHeaders = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type',
};

function jsonResponse(data: any, status = 200) {
	return new Response(JSON.stringify(data), {
		status,
		headers: {
			'Content-Type': 'application/json',
			...corsHeaders
		}
	});
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		if (request.method === 'OPTIONS') {
			return new Response(null, { headers: corsHeaders });
		}

		const url = new URL(request.url);
		const path = url.pathname;

		try {
			if (path === '/' || path === '/health') {
				return jsonResponse({
					status: 'ok',
					service: 'synthetic-market-research-backend',
					environment: env.ENVIRONMENT || 'production'
				});
			}

			if (path === '/api/session/create' && request.method === 'POST') {
				return await handleCreateSession(request, env, ctx);
			}

			if (path.startsWith('/api/session/') && path.endsWith('/data') && request.method === 'GET') {
				const sessionId = path.split('/')[3];
				return await handleGetSession(sessionId, env);
			}

			if (path.startsWith('/api/session/') && path.endsWith('/chat') && request.method === 'POST') {
				const sessionId = path.split('/')[3];
				return await handleChat(sessionId, request, env);
			}

			return jsonResponse({ error: 'Not found' }, 404);
		} catch (error) {
			console.error('Worker error:', error);
			return jsonResponse({
				error: 'Internal server error',
				message: error instanceof Error ? error.message : 'Unknown error'
			}, 500);
		}
	}
};

async function handleCreateSession(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
	const body = await request.json<CreateSessionRequest>();
	
	if (!body.image) {
		return jsonResponse({ error: 'Image is required' }, 400);
	}

	const sessionId = crypto.randomUUID();

	const id = env.SESSIONS.idFromName(sessionId);
	const stub = env.SESSIONS.get(id);

	await stub.fetch('http://internal/create', {
		method: 'POST',
		body: JSON.stringify({
			sessionId,
			imageBase64: body.image
		})
	});

	ctx.waitUntil(
		(async () => {
			try {
				console.log('Starting evaluation with Python API:', env.PYTHON_API_URL);
				const results = await evaluateProduct(
					env.PYTHON_API_URL,
					body.image,
					body.demographics
				);

				console.log('Evaluation completed, results:', results.length);

				await stub.fetch('http://internal/evaluation-results', {
					method: 'POST',
					body: JSON.stringify({
						results,
						status: 'completed'
					})
				});
			} catch (error) {
				console.error('Evaluation error:', error);
				const errorMessage = error instanceof Error ? error.message : 'Unknown error';
				console.error('Error message:', errorMessage);
				
				await stub.fetch('http://internal/evaluation-results', {
					method: 'POST',
					body: JSON.stringify({
						results: [],
						status: 'error',
						error: errorMessage
					})
				});
			}
		})()
	);

	return jsonResponse({
		sessionId,
		status: 'processing',
		message: 'Evaluation started'
	});
}

async function handleGetSession(sessionId: string, env: Env): Promise<Response> {
	const id = env.SESSIONS.idFromName(sessionId);
	const stub = env.SESSIONS.get(id);

	const response = await stub.fetch('http://internal/data');
	
	return new Response(response.body, {
		status: response.status,
		headers: {
			...corsHeaders,
			'Content-Type': 'application/json'
		}
	});
}

async function handleChat(sessionId: string, request: Request, env: Env): Promise<Response> {
	const body = await request.json<ChatRequest>();
	
	if (!body.message) {
		return jsonResponse({ error: 'Message is required' }, 400);
	}

	const id = env.SESSIONS.idFromName(sessionId);
	const stub = env.SESSIONS.get(id) as any;

	await stub.fetch('http://internal/chat', {
		method: 'POST',
		body: JSON.stringify({ message: body.message })
	});

	const dataResponse = await stub.fetch('http://internal/data');
	const sessionData = await dataResponse.json() as any;

	if (!sessionData.evaluationResults || sessionData.evaluationResults.length === 0) {
		return jsonResponse({
			message: 'Please wait for the evaluation to complete before chatting.',
			timestamp: Date.now()
		});
	}

	const contextResponse = await stub.fetch('http://internal/evaluation-context');
	const contextData = await contextResponse.json() as { context: string };
	const evaluationContext = contextData.context;

	const aiResponse = await generateChatResponse(
		env.CLOUDFLARE_ACCOUNT_ID,
		env.CLOUDFLARE_API_KEY,
		evaluationContext,
		sessionData.chatHistory || [],
		body.message
	);

	await stub.fetch('http://internal/chat', {
		method: 'POST',
		body: JSON.stringify({ response: aiResponse })
	});

	return jsonResponse({
		message: aiResponse,
		timestamp: Date.now()
	});
}
