from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Model for a user
class User(BaseModel):
    id: int
    username: str

# Model to track a user's daily streak
class DailyStreak(BaseModel):
    user_id: int
    streak_date: datetime
    streak_count: int

# Simulating databases
users_db = []
streaks_db = []

# Route to register a user
@app.post("/api/register-user")
def register_user(user: User):
    if any(u.id == user.id for u in users_db):
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_db.append(user)
    return {"message": f"User {user.username} registered successfully!"}

# Route to get all users
@app.get("/api/users", response_model=List[User])
def get_users():
    if not users_db:
        raise HTTPException(status_code=404, detail="No users found")
    return users_db

# Route to update or check streak for a user
@app.post("/api/update-streak")
def update_streak(user_id: int):
    # Check if the user exists
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    today = datetime.today().date()

    # Check if there's already a streak record for today
    streak = next((s for s in streaks_db if s.user_id == user_id and s.streak_date.date() == today), None)

    if streak:
        # If a streak is already recorded today, return the streak count
        return {"message": f"Streak for {user.username} is already updated today!", "streak_count": streak.streak_count}
    
    # Get the most recent streak to calculate the streak count
    last_streak = next((s for s in streaks_db if s.user_id == user_id), None)
    if last_streak and last_streak.streak_date.date() == today - timedelta(days=1):
        # Continue streak if it's a consecutive day
        new_streak_count = last_streak.streak_count + 1
    else:
        # Start a new streak
        new_streak_count = 1
    
    # Create a new streak entry for today
    new_streak = DailyStreak(user_id=user_id, streak_date=datetime.today(), streak_count=new_streak_count)
    streaks_db.append(new_streak)

    return {"message": f"Streak updated for {user.username}!", "streak_count": new_streak_count}

# Route to get streak information for a user
@app.get("/api/streaks/{user_id}", response_model=List[DailyStreak])
def get_user_streaks(user_id: int):
    # Get all streaks for the user
    user_streaks = [s for s in streaks_db if s.user_id == user_id]
    if not user_streaks:
        raise HTTPException(status_code=404, detail="No streaks found for this user")
    return user_streaks

# Route to get the longest streak of a user
@app.get("/api/longest-streak/{user_id}")
def get_longest_streak(user_id: int):
    # Get all streaks for the user
    user_streaks = [s for s in streaks_db if s.user_id == user_id]
    if not user_streaks:
        raise HTTPException(status_code=404, detail="No streaks found for this user")

    # Find the longest streak
    longest_streak = max(user_streaks, key=lambda x: x.streak_count)
    return {
        "user_id": user_id,
        "longest_streak": longest_streak.streak_count,
        "streak_start_date": longest_streak.streak_date.date()
    }

# Root route with a welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to the Daily Streaks Microservice!"}

# Run the app using uvicorn (this can be done directly or using the command line)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
