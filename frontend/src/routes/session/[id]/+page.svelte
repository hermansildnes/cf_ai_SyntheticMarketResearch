<script lang="ts">
	import { page } from '$app/stores';
	import { onMount, onDestroy } from 'svelte';
	import { getSessionData, sendChatMessage } from '$lib/api/client';
	import type { SessionData, EvaluationResponse } from '$shared/types';

	const sessionId = $derived($page.params.id);
	
	let sessionData = $state<SessionData | null>(null);
	let chatMessages = $state<Array<{ role: 'user' | 'assistant', content: string }>>([]);
	let userInput = $state('');
	let isLoading = $state(true);
	let isSending = $state(false);
	let errorMessage = $state('');
	let pollingInterval: number | null = null;

	const isProcessing = $derived(sessionData?.status === 'processing');
	const isCompleted = $derived(sessionData?.status === 'completed');
	const hasError = $derived(sessionData?.status === 'error');
	const evaluationResults = $derived(sessionData?.evaluationResults || []);
	const overallRating = $derived(() => {
		if (!evaluationResults.length) return 0;
		const sum = evaluationResults.reduce((acc, r) => acc + r.mean_rating, 0);
		return (sum / evaluationResults.length).toFixed(1);
	});

	onMount(async () => {
		await loadSessionData();
		
		if (sessionData?.status === 'processing') {
			startPolling();
		}
	});

	onDestroy(() => {
		stopPolling();
	});

	async function loadSessionData() {
		try {
			const data = await getSessionData(sessionId);
			sessionData = data;
			chatMessages = data.chatHistory.map(msg => ({
				role: msg.role,
				content: msg.content
			}));
			isLoading = false;

			if (data.status !== 'processing') {
				stopPolling();
			}
		} catch (error) {
			console.error('Failed to load session:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to load session';
			isLoading = false;
			stopPolling();
		}
	}

	function startPolling() {
		pollingInterval = window.setInterval(async () => {
			await loadSessionData();
		}, 2000);
	}

	function stopPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval);
			pollingInterval = null;
		}
	}

	async function sendMessage() {
		if (!userInput.trim() || isSending || !isCompleted) return;

		const message = userInput.trim();
		userInput = '';
		
		chatMessages = [...chatMessages, { role: 'user', content: message }];
		isSending = true;
		errorMessage = '';

		try {
			const response = await sendChatMessage(sessionId, message);
			
			chatMessages = [...chatMessages, { 
				role: 'assistant', 
				content: response.message 
			}];
		} catch (error) {
			console.error('Failed to send message:', error);
			errorMessage = 'Failed to send message. Please try again.';
			chatMessages = chatMessages.slice(0, -1);
			userInput = message;
		} finally {
			isSending = false;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}
</script>

<svelte:head>
	<title>Session {sessionId} - Synthetic Market Research</title>
</svelte:head>

<div class="session-container">
	<div class="session-header">
		<h1>Evaluation Results</h1>
		<div class="session-id">Session ID: {sessionId}</div>
	</div>

	{#if errorMessage}
		<div class="error-banner">
			<strong>Error:</strong> {errorMessage}
			<button onclick={() => window.location.reload()}>Retry</button>
		</div>
	{/if}

	{#if isLoading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading session data...</p>
		</div>
	{:else if hasError}
		<div class="error-state">
			<div class="error-icon">❌</div>
			<h2>Evaluation Failed</h2>
			<p>There was an error processing your product evaluation.</p>
			{#if sessionData?.error}
				<div class="error-details">
					<strong>Error details:</strong> {sessionData.error}
				</div>
			{/if}
			<a href="/" class="back-button">Upload Another Image</a>
		</div>
	{:else if isProcessing}
		<div class="processing-state">
			<div class="spinner"></div>
			<h2>Analyzing Your Product...</h2>
			<p>Our AI is evaluating your product with synthetic consumer personas.</p>
			<p class="hint">This typically takes 15-30 seconds. The page will update automatically.</p>
		</div>
	{:else if isCompleted && evaluationResults.length > 0}
		<div class="content-grid">
			<div class="results-panel">
				<div class="card">
					<h2>Overall Rating</h2>
					<div class="overall-rating">
						<span class="rating-number">{overallRating()}</span>
						<span class="rating-scale">/ 5.0</span>
					</div>
					<p class="rating-subtitle">
						Based on {evaluationResults.length} demographic profile{evaluationResults.length > 1 ? 's' : ''}
					</p>
				</div>

				<div class="card">
					<h2>Demographic Breakdown</h2>
					<div class="demographics">
						{#each evaluationResults as result}
							{@const profile = result.demographic_profile}
							<div class="demo-item">
								<div class="demo-info">
									<strong>{profile.age}yo {profile.gender}</strong>
									<span class="location">{profile.location}</span>
									<span class="occupation">{profile.occupation}</span>
								</div>
								<div class="demo-rating">
									<span class="rating">{result.mean_rating.toFixed(1)}</span>
									<div class="rating-bar">
										<div class="rating-fill" style="width: {(result.mean_rating / 5) * 100}%"></div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<div class="card">
					<h2>Detailed Feedback</h2>
					<div class="feedback-list">
						{#each evaluationResults as result, index}
							{@const profile = result.demographic_profile}
							<details class="feedback-item">
								<summary>
									<strong>{profile.age}yo {profile.gender}</strong> - {profile.occupation}
									<span class="feedback-rating">{result.mean_rating.toFixed(1)} ⭐</span>
								</summary>
								<div class="feedback-content">
									<p>{result.response}</p>
								</div>
							</details>
						{/each}
					</div>
				</div>
			</div>

			<div class="chat-panel">
				<div class="card chat-card">
					<h2>Ask AI About Results</h2>
					
					<div class="chat-messages">
						{#if chatMessages.length === 0}
							<div class="chat-empty">
								<p>💬 Ask questions about your product evaluation:</p>
								<ul>
									<li>"How should I change the product?"</li>
									<li>"Which demographic liked it most?"</li>
									<li>"What were the main concerns?"</li>
									<li>"How can I improve the rating?"</li>
								</ul>
							</div>
						{:else}
							{#each chatMessages as message}
								<div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
									<div class="message-content">
										{message.content}
									</div>
								</div>
							{/each}
						{/if}
						{#if isSending}
							<div class="message assistant">
								<div class="message-content">
									<div class="typing-indicator">
										<span></span><span></span><span></span>
									</div>
								</div>
							</div>
						{/if}
					</div>

					<div class="chat-input">
						<textarea
							bind:value={userInput}
							onkeypress={handleKeyPress}
							placeholder="Ask a question..."
							rows="2"
							disabled={isSending}
						></textarea>
						<button onclick={sendMessage} disabled={!userInput.trim() || isSending}>
							Send
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.session-container {
		max-width: 1200px;
		margin: 0 auto;
	}

	.session-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}

	.session-header h1 {
		margin: 0;
		font-size: 2rem;
	}

	.session-id {
		color: #6b7280;
		font-size: 0.875rem;
		font-family: monospace;
	}

	.loading {
		text-align: center;
		padding: 4rem;
	}

	.error-banner {
		background: #fef2f2;
		border: 1px solid #fecaca;
		padding: 1rem;
		border-radius: 8px;
		color: #dc2626;
		margin-bottom: 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.error-banner button {
		padding: 0.5rem 1rem;
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
	}

	.error-state,
	.processing-state {
		text-align: center;
		padding: 4rem;
	}

	.error-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.error-state h2,
	.processing-state h2 {
		color: #1f2937;
		margin-bottom: 1rem;
	}

	.error-state p,
	.processing-state p {
		color: #6b7280;
		margin-bottom: 0.5rem;
	}

	.hint {
		font-size: 0.875rem;
		font-style: italic;
	}

	.back-button {
		display: inline-block;
		margin-top: 2rem;
		padding: 0.75rem 1.5rem;
		background: #3b82f6;
		color: white;
		text-decoration: none;
		border-radius: 8px;
		font-weight: 600;
	}

	.back-button:hover {
		background: #2563eb;
	}

	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
		}
	}

	.card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		margin-bottom: 1.5rem;
	}

	.card h2 {
		margin: 0 0 1rem 0;
		font-size: 1.25rem;
		color: #1f2937;
	}

	.overall-rating {
		text-align: center;
		padding: 2rem;
	}

	.rating-number {
		font-size: 4rem;
		font-weight: bold;
		color: #3b82f6;
	}

	.rating-scale {
		font-size: 1.5rem;
		color: #9ca3af;
		margin-left: 0.5rem;
	}

	.rating-subtitle {
		text-align: center;
		color: #6b7280;
		font-size: 0.875rem;
		margin-top: 1rem;
	}

	.demographics {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.demo-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 8px;
	}

	.demo-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.location,
	.occupation {
		font-size: 0.875rem;
		color: #6b7280;
	}

	.demo-rating {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.5rem;
		min-width: 120px;
	}

	.rating {
		font-weight: 600;
		color: #3b82f6;
	}

	.rating-bar {
		width: 100%;
		height: 6px;
		background: #e5e7eb;
		border-radius: 3px;
		overflow: hidden;
	}

	.rating-fill {
		height: 100%;
		background: #3b82f6;
		transition: width 0.3s;
	}

	.feedback-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.feedback-item {
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		overflow: hidden;
	}

	.feedback-item summary {
		padding: 1rem;
		cursor: pointer;
		background: #f9fafb;
		display: flex;
		justify-content: space-between;
		align-items: center;
		user-select: none;
	}

	.feedback-item summary:hover {
		background: #f3f4f6;
	}

	.feedback-rating {
		font-weight: 600;
		color: #3b82f6;
	}

	.feedback-content {
		padding: 1rem;
		background: white;
		line-height: 1.6;
	}

	.feedback-content p {
		margin: 0;
		color: #374151;
	}

	.chat-card {
		height: calc(100vh - 300px);
		min-height: 500px;
		display: flex;
		flex-direction: column;
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		margin-bottom: 1rem;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 8px;
	}

	.chat-empty {
		text-align: center;
		color: #6b7280;
		padding: 2rem;
	}

	.chat-empty ul {
		text-align: left;
		display: inline-block;
		margin-top: 1rem;
	}

	.message {
		margin-bottom: 1rem;
		display: flex;
	}

	.message.user {
		justify-content: flex-end;
	}

	.message-content {
		max-width: 80%;
		padding: 0.75rem 1rem;
		border-radius: 12px;
		line-height: 1.5;
	}

	.message.user .message-content {
		background: #3b82f6;
		color: white;
	}

	.message.assistant .message-content {
		background: white;
		border: 1px solid #e5e7eb;
	}

	.typing-indicator {
		display: flex;
		gap: 4px;
	}

	.typing-indicator span {
		width: 8px;
		height: 8px;
		background: #9ca3af;
		border-radius: 50%;
		animation: bounce 1.4s infinite ease-in-out both;
	}

	.typing-indicator span:nth-child(1) {
		animation-delay: -0.32s;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}

	.chat-input {
		display: flex;
		gap: 0.5rem;
	}

	.chat-input textarea {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-family: inherit;
		font-size: 1rem;
		resize: none;
	}

	.chat-input textarea:focus {
		outline: none;
		border-color: #3b82f6;
	}

	.chat-input button {
		padding: 0.75rem 1.5rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.chat-input button:hover:not(:disabled) {
		background: #2563eb;
	}

	.chat-input button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
