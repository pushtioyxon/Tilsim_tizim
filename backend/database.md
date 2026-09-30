# Database

Users:
- id: int (PK)
- phone: str (unique)
- password_hash: str
- created_at: datetime

Profiles:
- id: int (PK)
- user_id: int (FK -> Users.id)
- first_name: str
- last_name: str | null
- bio: str | null
- avatar_id: int | null (FK -> Files.id)

Files:
- id: int (PK)
- storage_key: str (unique)
- original_name: str
- mime_type: str
- size_bytes: bigint
- media_type: "video" | "image" | "audio" | null
- width: int | null
- height: int | null
- thumbnail_parent_id: int | null (FK -> Files.id)
- created_at: datetime

Quizzes:
- id: int (PK)
- owner_id: int (FK -> Users.id)
- title: str
- status: "private" | "public" = "private"
- description: str | null
- created_at: datetime

Questions:
- id: int (PK)
- quiz_id: int (FK -> Quizzes.id)
- order: int
- text: str
- type: "single" | "multiple" | "matching"

Options:
- id: int (PK)
- question_id: int (FK -> Questions.id)
- text: str
- order: int
- is_correct: bool

QuestionPairs:
- id: int (PK)
- question_id: int (FK -> Questions.id)
- left_text: str
- right_text: str
- order: int

QuizAttempts:
- id: int (PK)
- quiz_id: int (FK -> Quizzes.id)
- user_id: int (FK -> Users.id)
- started_at: datetime
- finished_at: datetime | null

AttemptAnswers:
- id: int (PK)
- attempt_id: int (FK -> QuizAttempts.id)
- question_id: int (FK -> Questions.id)
- option_id: int | null (FK -> Options.id)
- is_correct: bool | null
- matching_pairs: json | null

```json
[
    {
        "pair_id": int (FK -> QuestionPairs.id),
        "selected_right_pair_id": int (FK -> QuestionPairs.id)
    },
]
```
