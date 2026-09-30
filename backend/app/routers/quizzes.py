from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.entities import User, Quiz, Question, Option, QuestionPair
from app.schemas.schemas import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizDetailResponse,
    QuestionCreate,
    QuestionResponse
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.get("/", response_model=List[QuizResponse])
def get_quizzes(
    status: Optional[str] = "public",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Quiz)
    if status:
        query = query.filter(Quiz.status == status)
    quizzes = query.offset(skip).limit(limit).all()
    
    # Calculate questions_count
    results = []
    for q in quizzes:
        q_dict = {
            "id": q.id,
            "owner_id": q.owner_id,
            "title": q.title,
            "status": q.status,
            "description": q.description,
            "created_at": q.created_at,
            "questions_count": len(q.questions)
        }
        results.append(QuizResponse(**q_dict))
    return results

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz_in: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = Quiz(
        owner_id=current_user.id,
        title=quiz_in.title,
        status=quiz_in.status,
        description=quiz_in.description
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return QuizResponse(
        id=quiz.id,
        owner_id=quiz.owner_id,
        title=quiz.title,
        status=quiz.status,
        description=quiz.description,
        created_at=quiz.created_at,
        questions_count=0
    )

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def get_quiz_detail(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz topilmadi")
    
    return quiz

@router.post("/{quiz_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def add_question(
    quiz_id: int,
    question_in: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz topilmadi")
    if quiz.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Faqat quiz egasi savol qo'sha oladi")
    
    question = Question(
        quiz_id=quiz.id,
        order=question_in.order,
        text=question_in.text,
        type=question_in.type
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Add options if single/multiple choice
    if question_in.options:
        for opt in question_in.options:
            db_opt = Option(
                question_id=question.id,
                text=opt.text,
                order=opt.order,
                is_correct=opt.is_correct
            )
            db.add(db_opt)

    # Add pairs if matching type
    if question_in.pairs:
        for pair in question_in.pairs:
            db_pair = QuestionPair(
                question_id=question.id,
                left_text=pair.left_text,
                right_text=pair.right_text,
                order=pair.order
            )
            db.add(db_pair)

    db.commit()
    db.refresh(question)
    return question
