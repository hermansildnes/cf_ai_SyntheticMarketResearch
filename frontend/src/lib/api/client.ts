// API client for interacting with the backend
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8788';

import type {
	DemographicProfile,
	CreateSessionRequest,
	CreateSessionResponse,
	SessionData,
	ChatRequest,
	ChatResponse
} from '$shared/types';

export type { DemographicProfile };

export async function fileToBase64(file: File): Promise<string> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onload = () => {
			const base64 = (reader.result as string).split(',')[1];
			resolve(base64);
		};
		reader.onerror = reject;
		reader.readAsDataURL(file);
	});
}

export async function createSession(
	imageBase64: string,
	demographics?: DemographicProfile[]
): Promise<CreateSessionResponse> {
	const payload: CreateSessionRequest = {
		image: imageBase64,
		demographics
	};

	const response = await fetch(`${BACKEND_URL}/api/session/create`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(payload)
	});

	if (!response.ok) {
		const error = await response.text();
		throw new Error(`Failed to create session: ${error}`);
	}

	return await response.json();
}


export async function getSessionData(sessionId: string): Promise<SessionData> {
	const response = await fetch(`${BACKEND_URL}/api/session/${sessionId}/data`);

	if (!response.ok) {
		if (response.status === 404) {
			throw new Error('Session not found');
		}
		throw new Error('Failed to fetch session data');
	}

	return await response.json();
}


export async function waitForEvaluation(
	sessionId: string,
	onProgress?: (status: string) => void,
	maxAttempts = 60,
	intervalMs = 2000
): Promise<SessionData> {
	for (let i = 0; i < maxAttempts; i++) {
		const data = await getSessionData(sessionId);

		if (onProgress) {
			onProgress(data.status);
		}

		if (data.status === 'completed') {
			return data;
		}

		if (data.status === 'error') {
			throw new Error('Evaluation failed');
		}

		await new Promise((resolve) => setTimeout(resolve, intervalMs));
	}

	throw new Error('Evaluation timeout');
}

export async function sendChatMessage(
	sessionId: string,
	message: string
): Promise<ChatResponse> {
	const payload: ChatRequest = {
		message
	};

	const response = await fetch(`${BACKEND_URL}/api/session/${sessionId}/chat`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(payload)
	});

	if (!response.ok) {
		throw new Error('Failed to send chat message');
	}

	return await response.json();
}
