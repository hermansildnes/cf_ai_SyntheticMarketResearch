#!/bin/bash

set -e

if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your Cloudflare credentials"
    exit 1
fi

source .env

if [[ "$CLOUDFLARE_API_KEY" == "your_api_key_here" ]] || [[ -z "$CLOUDFLARE_API_KEY" ]]; then
    echo "CLOUDFLARE_API_KEY not set in .env"
    exit 1
fi

if [[ "$CLOUDFLARE_ACCOUNT_ID" == "your_account_id_here" ]] || [[ -z "$CLOUDFLARE_ACCOUNT_ID" ]]; then
    echo "CLOUDFLARE_ACCOUNT_ID not set in .env"
    exit 1
fi

cat > api/.dev.vars << EOF
CLOUDFLARE_API_KEY=$CLOUDFLARE_API_KEY
CLOUDFLARE_ACCOUNT_ID=$CLOUDFLARE_ACCOUNT_ID
EOF

cat > backend/.dev.vars << EOF
PYTHON_API_URL=http://localhost:8787
ENVIRONMENT=development
EOF

cat > frontend/.env << EOF
VITE_BACKEND_URL=http://localhost:8788
EOF

trap 'jobs -p | xargs -r kill 2>/dev/null' EXIT

echo "Starting services..."

(cd backend && npm run dev > /dev/null 2>&1) &
sleep 2

(cd api && npx wrangler dev > /dev/null 2>&1) &
sleep 2

(cd frontend && npm run dev > /dev/null 2>&1) &
sleep 3

echo ""
echo "Ready: http://localhost:5173"

wait
