# source C://ProgramData//anaconda3//etc//profile.d//conda.sh
# conda activate tender_data_extractor

source ../venv-tenders/Scripts/activate

export PYTHONPATH="$(pwd)/backend"

# Start FastAPI app
uvicorn backend.main:app &
FASTAPI_PID=$!

# Navigate to the frontend directory and start the frontend
cd ./frontend  # Replace with the actual path to your frontend directory
npm run dev &
FRONTEND_PID=$!

# Wait for either process to exit
wait -n $FASTAPI_PID $FRONTEND_PID

# Cleanup
kill $FASTAPI_PID $FRONTEND_PID