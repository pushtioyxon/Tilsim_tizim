from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field

# --- Auth & User Schemas ---
class SendOTPRequest(BaseModel):
    phone: str = Field(..., example="+998901234567")

class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., example="+998901234567")
    code: str = Field(..., example="000000")

class OTPResponse(BaseModel):
    message: str
    phone: str
    dev_code: Optional[str] = "000000"

class UserRegister(BaseModel):
    phone: str = Field(..., example="+998901234567")
    password: str = Field(..., min_length=4, example="Secret123")
    first_name: str = Field(..., example="Ali")
    last_name: Optional[str] = Field(None, example="Valiyev")
    otp_code: Optional[str] = Field("000000", example="000000")

class UserLogin(BaseModel):
    phone: str = Field(..., example="+998901234567")
    password: str = Field(..., example="Secret123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: Optional[bool] = False

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    phone: str
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

# --- File Schemas ---
class FileResponse(BaseModel):
    id: int
    storage_key: str
    original_name: str
    mime_type: str
    size_bytes: int
    media_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Option Schemas ---
class OptionBase(BaseModel):
    text: str
    order: int = 0
    is_correct: bool = False

class OptionCreate(OptionBase):
    pass

class OptionResponse(OptionBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

# Public Option Response for students taking the test (without is_correct)
class OptionPublicResponse(BaseModel):
    id: int
    text: str
    order: int

    class Config:
        from_attributes = True

# --- Question Pair Schemas ---
class QuestionPairBase(BaseModel):
    left_text: str
    right_text: str
    order: int = 0

class QuestionPairCreate(QuestionPairBase):
    pass

class QuestionPairResponse(QuestionPairBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    order: int = 0
    text: str
    type: Literal["single", "multiple", "matching"]

class QuestionCreate(QuestionBase):
    options: Optional[List[OptionCreate]] = []
    pairs: Optional[List[QuestionPairCreate]] = []

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    options: List[OptionResponse] = []
    pairs: List[QuestionPairResponse] = []

    class Config:
        from_attributes = True

class QuestionPublicResponse(QuestionBase):
    id: int
    quiz_id: int
    options: List[OptionPublicResponse] = []
    pairs: List[QuestionPairResponse] = []

    class Config:
        from_attributes = True

# --- Quiz Schemas ---
class QuizBase(BaseModel):
    title: str
    status: Literal["private", "public"] = "private"
    description: Optional[str] = None

class QuizCreate(QuizBase):
    pass

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[Literal["private", "public"]] = None
    description: Optional[str] = None

class QuizResponse(QuizBase):
    id: int
    owner_id: int
    created_at: datetime
    questions_count: Optional[int] = 0

    class Config:
        from_attributes = True

class QuizDetailResponse(QuizResponse):
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

# --- Quiz Attempt & Answer Schemas ---
class MatchingPairItem(BaseModel):
    pair_id: int
    selected_right_pair_id: int

class AnswerSubmit(BaseModel):
    question_id: int
    option_id: Optional[int] = None
    matching_pairs: Optional[List[MatchingPairItem]] = None

class AttemptStart(BaseModel):
    quiz_id: int

class AttemptAnswerResponse(BaseModel):
    id: int
    question_id: int
    option_id: Optional[int] = None
    is_correct: Optional[bool] = None
    matching_pairs: Optional[Any] = None

    class Config:
        from_attributes = True

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    total_questions: Optional[int] = 0
    correct_answers: Optional[int] = 0
    score_percent: Optional[float] = 0.0

    class Config:
        from_attributes = True
