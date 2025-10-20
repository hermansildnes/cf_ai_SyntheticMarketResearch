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

export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_KEY
export CLOUDFLARE_ACCOUNT_ID=$CLOUDFLARE_ACCOUNT_ID

echo "Checking dependencies..."

if [ ! -d "api/node_modules" ]; then
    echo "Installing wrangler for API..."
    (cd api && npm install wrangler)
fi

if [ ! -d "backend/node_modules" ]; then
    echo "Installing backend dependencies..."
    (cd backend && npm install)
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd frontend && npm install)
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

mkdir -p logs

(cd backend && npm run dev > ../logs/backend.log 2>&1) &
BACKEND_PID=$!
sleep 2

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start. Check logs/backend.log"
    exit 1
fi

(cd api && npx wrangler dev > ../logs/api.log 2>&1) &
API_PID=$!
sleep 2

if ! kill -0 $API_PID 2>/dev/null; then
    echo "API failed to start. Check logs/api.log"
    exit 1
fi

(cd frontend && npm run dev > ../logs/frontend.log 2>&1) &
FRONTEND_PID=$!
sleep 2

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "Frontend failed to start. Check logs/frontend.log"
    exit 1
fi

echo ""
echo "Ready: http://localhost:5173"
echo ""

wait
