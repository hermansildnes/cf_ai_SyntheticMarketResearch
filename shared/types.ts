export interface DemographicProfile {
	age: number;
	gender: string;
	location: string;
	income: string;
	occupation: string;
	interests: string[];
}

export interface EvaluationRequest {
	image: string;
	demographic_profile: DemographicProfile;
}

export interface EvaluationResponse {
	success: boolean;
	demographic_profile: DemographicProfile;
	response: string;
	distributions: number[][];
	mean_rating: number;
}

export interface ChatMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: number;
}

export interface SessionData {
	id: string;
	imageBase64: string;
	status: 'uploading' | 'processing' | 'completed' | 'error';
	evaluationResults?: EvaluationResponse[];
	chatHistory: ChatMessage[];
	error?: string;
	createdAt: number;
	updatedAt: number;
}

export interface CreateSessionRequest {
	image: string;
	demographics?: DemographicProfile[];
}

export interface CreateSessionResponse {
	sessionId: string;
	status: string;
}

export interface ChatRequest {
	message: string;
}

export interface ChatResponse {
	message: string;
	timestamp: number;
}
