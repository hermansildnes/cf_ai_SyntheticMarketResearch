<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	let { children } = $props();
</script>

<div class="app">
	<header>
		<nav>
			<a href="/" class="logo">
				<span class="icon">🔬</span>
				<span>Synthetic Market Research</span>
			</a>
		</nav>
	</header>

	<main>
		{@render children()}
	</main>

	<footer>
		<p>Build with Cloudflare Workers and Workers AI</p>
	</footer>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	header {
		padding: 1rem 2rem;
		border-bottom: 1px solid #e5e7eb;
		background: white;
	}

	nav {
		max-width: 1200px;
		margin: 0 auto;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: #1f2937;
		text-decoration: none;
	}

	.logo .icon {
		font-size: 1.5rem;
	}

	main {
		flex: 1;
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	footer {
		padding: 1rem;
		text-align: center;
		border-top: 1px solid #e5e7eb;
		color: #6b7280;
		font-size: 0.875rem;
	}

	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
			Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
		background: #f9fafb;
		color: #1f2937;
	}

	:global(*) {
		box-sizing: border-box;
	}
</style>
