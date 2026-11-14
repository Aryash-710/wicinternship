from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query, status
from app.models.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, AuthTokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & User Profiles"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest):
    """
    Registers a new Worker or Employer account.
    - If Worker: automatically provisions or links a Worker profile in the database.
    - Returns an active session token and user profile.
    """
    try:
        user = AuthService.register_user(
            username=req.username,
            phone=req.phone,
            password=req.password,
            role=req.role,
            full_name=req.full_name,
            city=req.city,
            trade=req.trade,
            daily_rate=req.daily_rate,
            experience_years=req.experience_years,
            company_name=req.company_name
        )
        token = AuthService.create_session(user["id"])
        return AuthTokenResponse(token=token, user=UserResponse(**user), message="Registration successful")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=AuthTokenResponse)
def login(req: UserLoginRequest):
    """
    Authenticates a Worker or Employer using username/phone and password.
    Returns session token and role details ('worker' or 'employer').
    """
    user = AuthService.authenticate(req.username_or_phone, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your username/phone and password."
        )

    token = AuthService.create_session(user["id"])
    return AuthTokenResponse(
        token=token,
        user=UserResponse(**user),
        message=f"Welcome back, {user['full_name']}! Signed in as {user['role'].upper()}."
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    """
    Retrieves the authenticated user's profile and active role based on bearer token.
    """
    active_token = authorization or token
    if not active_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token missing")

    user = AuthService.get_user_by_token(active_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token")

    return UserResponse(**user)


@router.post("/logout")
def logout(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    """
    Terminates the user's active session.
    """
    active_token = authorization or token
    if active_token:
        AuthService.logout(active_token)
    return {"status": "success", "message": "Logged out successfully"}


@router.get("/demo-users", response_model=List[UserResponse])
def get_demo_users():
    """
    Returns quick-access demo accounts for 1-click evaluation of Worker vs Employer views.
    """
    users = AuthService.get_demo_accounts()
    return [UserResponse(**u) for u in users]

