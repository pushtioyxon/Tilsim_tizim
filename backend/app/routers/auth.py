from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.entities import User, Profile
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse
)

router = APIRouter(prefix="/auth", tags=["Auth"])

def is_valid_mock_otp(code: str) -> bool:
    """
    Eskiz.uz ulanmaguncha faqat nollardan iborat kodlarni ('0000', '000000') qabul qiladi.
    """
    stripped = code.strip()
    return bool(stripped and set(stripped) == {"0"} and 4 <= len(stripped) <= 8)


@router.post("/send-otp", response_model=OTPResponse)
def send_otp(request: SendOTPRequest):
    """
    SMS orqali OTP kod yuborish (Hozircha Eskiz ulanmagani sababli kod: 000000)
    """
    return OTPResponse(
        message="Tasdiqlash kodi yuborildi. (Test rejimida: 000000)",
        phone=request.phone,
        dev_code="000000"
    )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    OTP kodni tekshirish va tizimga kirish (Kodni '000000' yoki '0000' deb kiritish kifoya)
    """
    if not is_valid_mock_otp(request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasdiqlash kodi noto'g'ri. Test rejimida '000000' kiriting."
        )

    user = db.query(User).filter(User.phone == request.phone).first()
    is_new = False

    if not user:
        # Yangi foydalanuvchi avtomatik ochiladi
        user = User(
            phone=request.phone,
            password_hash=hash_password("000000")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = Profile(
            user_id=user.id,
            first_name="Foydalanuvchi",
            last_name=None
        )
        db.add(profile)
        db.commit()
        db.refresh(user)
        is_new = True

    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_new_user": is_new
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # OTP kod kiritilgan bo'lsa, tekshiramiz
    if user_in.otp_code and not is_valid_mock_otp(user_in.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP kodi noto'g'ri. Hozircha '000000' kiriting."
        )

    existing_user = db.query(User).filter(User.phone == user_in.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu telefon raqam allaqachon ro'yxatdan o'tgan"
        )
    
    new_user = User(
        phone=user_in.phone,
        password_hash=hash_password(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Profil yaratish
    profile = Profile(
        user_id=new_user.id,
        first_name=user_in.first_name,
        last_name=user_in.last_name
    )
    db.add(profile)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == user_in.phone).first()
    
    # Parol to'g'riligini tekshirish:
    # 1. Asl o'rnatilgan parol to'g'ri kelsa
    # 2. YOKI parol o'rniga hammasi 0 bo'lgan kod ("0000", "000000") kiritilgan bo'lsa ham qabul qilinadi
    is_valid_pwd = user and (
        verify_password(user_in.password, user.password_hash) or
        is_valid_mock_otp(user_in.password)
    )

    if not is_valid_pwd:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon raqam yoki parol noto'g'ri (yoki '000000' kiriting)"
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "is_new_user": False}


# Swagger OAuth2 form login
@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == form_data.username).first()
    is_valid_pwd = user and (
        verify_password(form_data.password, user.password_hash) or
        is_valid_mock_otp(form_data.password)
    )
    if not is_valid_pwd:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon raqam yoki parol noto'g'ri"
        )
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "is_new_user": False}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
