from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.entities import User, Quiz, Question, Option, QuestionPair, QuizAttempt, AttemptAnswer
from app.schemas.schemas import (
    AttemptStart,
    AnswerSubmit,
    AttemptAnswerResponse,
    QuizAttemptResponse
)

router = APIRouter(prefix="/attempts", tags=["Quiz Attempts"])

@router.post("/start", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
def start_attempt(
    attempt_in: AttemptStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == attempt_in.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz topilmadi")

    new_attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        started_at=datetime.now(timezone.utc)
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    total_q = len(quiz.questions)
    return QuizAttemptResponse(
        id=new_attempt.id,
        quiz_id=new_attempt.quiz_id,
        user_id=new_attempt.user_id,
        started_at=new_attempt.started_at,
        finished_at=new_attempt.finished_at,
        total_questions=total_q,
        correct_answers=0,
        score_percent=0.0
    )

@router.post("/{attempt_id}/answer", response_model=AttemptAnswerResponse)
def submit_answer(
    attempt_id: int,
    answer_in: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Urinish (attempt) topilmadi")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat berilmagan")
    if attempt.finished_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ushbu test urinishi allaqachon yakunlangan")

    question = db.query(Question).filter(Question.id == answer_in.question_id, Question.quiz_id == attempt.quiz_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savol topilmadi")

    # Determine correctness
    is_correct = False
    matching_pairs_json = None

    if question.type in ["single", "multiple"]:
        if answer_in.option_id:
            option = db.query(Option).filter(Option.id == answer_in.option_id, Option.question_id == question.id).first()
            if option and option.is_correct:
                is_correct = True
    elif question.type == "matching":
        if answer_in.matching_pairs:
            matching_pairs_json = [item.model_dump() for item in answer_in.matching_pairs]
            # Validating matching: each pair_id should match selected_right_pair_id
            all_correct = True
            for item in answer_in.matching_pairs:
                if item.pair_id != item.selected_right_pair_id:
                    all_correct = False
                    break
            is_correct = all_correct

    # Upsert answer for this question in this attempt
    existing_answer = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == attempt.id,
        AttemptAnswer.question_id == question.id
    ).first()

    if existing_answer:
        existing_answer.option_id = answer_in.option_id
        existing_answer.is_correct = is_correct
        existing_answer.matching_pairs = matching_pairs_json
        db.commit()
        db.refresh(existing_answer)
        return existing_answer
    else:
        new_answer = AttemptAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            option_id=answer_in.option_id,
            is_correct=is_correct,
            matching_pairs=matching_pairs_json
        )
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
        return new_answer

@router.post("/{attempt_id}/finish", response_model=QuizAttemptResponse)
def finish_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Urinish (attempt) topilmadi")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat berilmagan")

    if attempt.finished_at is None:
        attempt.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(attempt)

    quiz = attempt.quiz
    total_q = len(quiz.questions)
    correct_count = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == attempt.id,
        AttemptAnswer.is_correct == True
    ).count()

    score_percent = round((correct_count / total_q * 100), 2) if total_q > 0 else 0.0

    return QuizAttemptResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        user_id=attempt.user_id,
        started_at=attempt.started_at,
        finished_at=attempt.finished_at,
        total_questions=total_q,
        correct_answers=correct_count,
        score_percent=score_percent
    )

@router.get("/{attempt_id}", response_model=QuizAttemptResponse)
def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Urinish (attempt) topilmadi")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat berilmagan")

    quiz = attempt.quiz
    total_q = len(quiz.questions)
    correct_count = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == attempt.id,
        AttemptAnswer.is_correct == True
    ).count()

    score_percent = round((correct_count / total_q * 100), 2) if total_q > 0 else 0.0

    return QuizAttemptResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        user_id=attempt.user_id,
        started_at=attempt.started_at,
        finished_at=attempt.finished_at,
        total_questions=total_q,
        correct_answers=correct_count,
        score_percent=score_percent
    )
