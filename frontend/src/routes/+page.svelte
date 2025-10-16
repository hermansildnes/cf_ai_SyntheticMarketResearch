<script lang="ts">
	import { goto } from '$app/navigation';
	import { createSession } from '$lib/api/client';

	let imageFile: File | null = $state(null);
	let imagePreview: string | null = $state(null);
	let base64Data: string | null = $state(null);
	let isDragging = $state(false);
	let isUploading = $state(false);
	let errorMessage = $state('');

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) processFile(file);
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		isDragging = false;
		
		const file = event.dataTransfer?.files[0];
		if (file?.type.startsWith('image/')) processFile(file);
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function processFile(file: File) {
		errorMessage = '';
		imageFile = file;
		
		const reader = new FileReader();
		reader.onload = (e) => {
			const result = e.target?.result as string;
			imagePreview = result;
			base64Data = result.split(',')[1];
		};
		reader.readAsDataURL(file);
	}

	async function handleSubmit() {
		if (!base64Data) return;

		isUploading = true;
		errorMessage = '';
		
		try {
			const response = await createSession(base64Data);
			goto(`/session/${response.sessionId}`);
		} catch (error) {
			console.error('Upload failed:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to upload image. Please try again.';
		} finally {
			isUploading = false;
		}
	}

	function clearImage() {
		imageFile = null;
		imagePreview = null;
		base64Data = null;
	}
</script>

<svelte:head>
	<title>Synthetic Market Research - Upload Product</title>
</svelte:head>

<div class="container">
	<div class="hero">
		<h1>AI-Powered Market Research</h1>
		<p class="subtitle">
			Upload a product image to get instant feedback from synthetic consumer personas across
			different demographics
		</p>
	</div>

	<div class="upload-card">
		<h2>Upload Product Image</h2>
		
		<div
			class="dropzone"
			class:dragging={isDragging}
			class:has-image={imagePreview}
			role="button"
			tabindex="0"
			ondrop={handleDrop}
			ondragover={handleDragOver}
			ondragleave={handleDragLeave}
		>
			{#if imagePreview}
				<img src={imagePreview} alt="Product preview" class="preview" />
				<button type="button" class="remove-btn" onclick={clearImage}>
					Remove
				</button>
			{:else}
				<div class="dropzone-content">
					<div class="icon">📸</div>
					<p class="instruction">Drag and drop an image here, or click to browse</p>
					<p class="hint">Supports: JPG, PNG, WebP</p>
				</div>
			{/if}
			
			<input
				type="file"
				accept="image/*"
				onchange={handleFileSelect}
				class="file-input"
			/>
		</div>

		{#if imageFile}
			<button
				type="button"
				class="submit-btn"
				disabled={isUploading}
				onclick={handleSubmit}
			>
				{isUploading ? 'Uploading...' : 'Start Analysis'}
			</button>
		{/if}

		{#if errorMessage}
			<div class="error-message">
				⚠️ {errorMessage}
			</div>
		{/if}
	</div>

	<div class="features">
		<div class="feature">
			<div class="feature-icon">🤖</div>
			<h3>AI-Powered Evaluation</h3>
			<p>Llama Vision models analyze your product from multiple perspectives</p>
		</div>
		<div class="feature">
			<div class="feature-icon">👥</div>
			<h3>Diverse Demographics</h3>
			<p>Get feedback from synthetic consumers across age, location, and interests</p>
		</div>
		<div class="feature">
			<div class="feature-icon">💬</div>
			<h3>Interactive Insights</h3>
			<p>Chat with AI to understand results and get actionable recommendations</p>
		</div>
	</div>
</div>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
	}

	.hero {
		text-align: center;
		margin-bottom: 3rem;
	}

	h1 {
		font-size: 2.5rem;
		margin: 0 0 1rem 0;
		color: #1f2937;
	}

	.subtitle {
		font-size: 1.125rem;
		color: #6b7280;
		line-height: 1.6;
	}

	.upload-card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		margin-bottom: 3rem;
	}

	.upload-card h2 {
		margin: 0 0 1.5rem 0;
		font-size: 1.5rem;
	}

	.dropzone {
		position: relative;
		border: 2px dashed #d1d5db;
		border-radius: 8px;
		padding: 3rem;
		text-align: center;
		transition: all 0.2s;
		cursor: pointer;
		min-height: 300px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.dropzone:hover {
		border-color: #9ca3af;
		background: #f9fafb;
	}

	.dropzone.dragging {
		border-color: #3b82f6;
		background: #eff6ff;
	}

	.dropzone.has-image {
		padding: 1rem;
		min-height: auto;
	}

	.dropzone-content {
		pointer-events: none;
	}

	.icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.instruction {
		font-size: 1.125rem;
		color: #374151;
		margin: 0 0 0.5rem 0;
	}

	.hint {
		font-size: 0.875rem;
		color: #9ca3af;
		margin: 0;
	}

	.file-input {
		position: absolute;
		inset: 0;
		opacity: 0;
		cursor: pointer;
	}

	.preview {
		max-width: 100%;
		max-height: 400px;
		border-radius: 8px;
		object-fit: contain;
	}

	.remove-btn {
		position: absolute;
		top: 1rem;
		right: 1rem;
		padding: 0.5rem 1rem;
		background: #ef4444;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.875rem;
	}

	.remove-btn:hover {
		background: #dc2626;
	}

	.submit-btn {
		width: 100%;
		margin-top: 1.5rem;
		padding: 1rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 1.125rem;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.submit-btn:hover:not(:disabled) {
		background: #2563eb;
	}

	.submit-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.error-message {
		margin-top: 1rem;
		padding: 1rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 6px;
		color: #dc2626;
		font-size: 0.875rem;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 2rem;
	}

	.feature {
		text-align: center;
	}

	.feature-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	.feature h3 {
		font-size: 1.125rem;
		margin: 0 0 0.5rem 0;
		color: #1f2937;
	}

	.feature p {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0;
		line-height: 1.5;
	}
</style>
