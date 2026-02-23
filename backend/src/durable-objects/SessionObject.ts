import { DurableObject } from 'cloudflare:workers';
import type { SessionData, ChatMessage, EvaluationResponse } from '../../../shared/types';

export class SessionObject extends DurableObject {
	private data: SessionData | null = null;
	private initialized = false;

	private async initialize() {
		if (this.initialized) return;
		
		const stored = await this.ctx.storage.get<SessionData>('session');
		this.data = stored || null;
		this.initialized = true;
	}

	private async save() {
		if (this.data) {
			this.data.updatedAt = Date.now();
			await this.ctx.storage.put('session', this.data);
		}
	}

	async fetch(request: Request): Promise<Response> {
		await this.initialize();

		const url = new URL(request.url);
		const path = url.pathname;

		try {
			if (request.method === 'POST' && path === '/create') {
				return await this.handleCreate(request);
			}

			if (request.method === 'GET' && path === '/data') {
				return await this.handleGetData();
			}

			if (request.method === 'POST' && path === '/evaluation-results') {
				return await this.handleSetEvaluationResults(request);
			}

			if (request.method === 'POST' && path === '/chat') {
				return await this.handleChat(request);
			}

			if (request.method === 'GET' && path === '/chat-history') {
				return await this.handleGetChatHistory();
			}

			if (request.method === 'GET' && path === '/evaluation-context') {
				return await this.handleGetEvaluationContext();
			}

			return new Response('Not found', { status: 404 });
		} catch (error) {
			console.error('SessionObject error:', error);
			return new Response(JSON.stringify({ error: 'Internal server error' }), {
				status: 500,
				headers: { 'Content-Type': 'application/json' }
			});
		}
	}

	private async handleCreate(request: Request): Promise<Response> {
		const { sessionId, imageBase64 } = await request.json<{ sessionId: string; imageBase64: string }>();

		this.data = {
			id: sessionId,
			imageBase64: '',
			status: 'processing',
			chatHistory: [],
			createdAt: Date.now(),
			updatedAt: Date.now()
		};

		await this.save();

		return new Response(JSON.stringify({ success: true }), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	private async handleGetData(): Promise<Response> {
		if (!this.data) {
			return new Response(JSON.stringify({ error: 'Session not found' }), {
				status: 404,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		const responseData = {
			...this.data,
			imageBase64: undefined
		};

		return new Response(JSON.stringify(responseData), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	private async handleSetEvaluationResults(request: Request): Promise<Response> {
		if (!this.data) {
			return new Response(JSON.stringify({ error: 'Session not found' }), {
				status: 404,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		const { results, status, error } = await request.json<{ 
			results: EvaluationResponse[]; 
			status: 'completed' | 'error';
			error?: string;
		}>();

		this.data.evaluationResults = results;
		this.data.status = status;
		
		if (error) {
			this.data.error = error;
		}
		
		await this.save();

		return new Response(JSON.stringify({ success: true }), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	private async handleChat(request: Request): Promise<Response> {
		if (!this.data) {
			return new Response(JSON.stringify({ error: 'Session not found' }), {
				status: 404,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		const { message, response } = await request.json<{ message?: string; response?: string }>();

		if (message) {
			const userMessage: ChatMessage = {
				role: 'user',
				content: message,
				timestamp: Date.now()
			};
			this.data.chatHistory.push(userMessage);
		}

		if (response) {
			// Add assistant response
			const assistantMessage: ChatMessage = {
				role: 'assistant',
				content: response,
				timestamp: Date.now()
			};
			this.data.chatHistory.push(assistantMessage);
		}

		await this.save();

		return new Response(JSON.stringify({ success: true }), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	private async handleGetChatHistory(): Promise<Response> {
		if (!this.data) {
			return new Response(JSON.stringify({ error: 'Session not found' }), {
				status: 404,
				headers: { 'Content-Type': 'application/json' }
			});
		}

		return new Response(JSON.stringify({ chatHistory: this.data.chatHistory }), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	private async handleGetEvaluationContext(): Promise<Response> {
		const context = await this.getEvaluationContext();
		return new Response(JSON.stringify({ context }), {
			headers: { 'Content-Type': 'application/json' }
		});
	}

	async getEvaluationContext(): Promise<string> {
		if (!this.data || !this.data.evaluationResults) {
			return 'No evaluation results available yet.';
		}

		const results = this.data.evaluationResults;
		let context = 'Product Evaluation Results:\n\n';

		results.forEach((result, index) => {
			const profile = result.demographic_profile;
			context += `Demographic ${index + 1}: ${profile.age}yo ${profile.gender} from ${profile.location}\n`;
			context += `Occupation: ${profile.occupation}, Income: ${profile.income}\n`;
			context += `Interests: ${profile.interests.join(', ')}\n`;
			context += `Rating: ${result.mean_rating}/5\n`;
			context += `Feedback: ${result.response}\n\n`;
		});

		return context;
	}
}
